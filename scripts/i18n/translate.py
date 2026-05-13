#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["ruamel.yaml>=0.18", "httpx>=0.27"]
# ///
"""AI translation pipeline for DesireCore market skills.

For each skill directory, ensure metadata.i18n contains every locale declared in
manifest.json/supportedLocales. When a target locale is missing or stale (its
source_hash differs from the current source body+strings hash), translate from
metadata.i18n.<source_locale>.body using an LLM.

Backends (auto-selected, in this priority):
  1. GitHub Models (default) — uses GITHUB_TOKEN with `models: read` permission,
     OpenAI-compatible chat-completions API at https://models.github.ai/inference.
     Model defaults to `openai/gpt-5-mini` (configure with TRANSLATE_MODEL).
  2. Anthropic API direct — used when ANTHROPIC_API_KEY is set AND
     TRANSLATE_BACKEND=anthropic. Endpoint https://api.anthropic.com/v1/messages.
     Model should be a Claude model id (e.g. claude-sonnet-4-6).

Translations preserve:
  - Markdown structure (heading hierarchy, list ordering, tables, fences)
  - Inline code, fenced code blocks, URLs, file paths
  - SVG, HTML tags, YAML keys
  - Glossary terms from scripts/i18n/glossary.json
  - Reserved words from glossary.do_not_translate

Output:
  - Updates metadata.i18n.<target_locale>.{name,short_desc,description,source_hash,
    translated_by,translated_at}
  - For target_locale == default_locale: writes the translated body to root SKILL.md
  - Otherwise: writes SKILL.<target_locale>.md

Usage:
  GITHUB_TOKEN=... scripts/i18n/translate.py                       # all stale locales
  scripts/i18n/translate.py skills/web-access                      # one skill
  scripts/i18n/translate.py --target en-US skills/web-access       # one locale
  scripts/i18n/translate.py --check                                # dry-run, exit 1 if stale
  scripts/i18n/translate.py --human                                # mark new translations as human (lock)

Env:
  GITHUB_TOKEN              required when backend=github (CI: provided automatically)
  ANTHROPIC_API_KEY         required when TRANSLATE_BACKEND=anthropic
  TRANSLATE_BACKEND         'github' (default) | 'anthropic'
  TRANSLATE_MODEL           backend-specific model id; default depends on backend
  TRANSLATE_ENDPOINT        override endpoint URL
  TRANSLATE_MAX_RETRIES     default 3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any

import httpx
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import FoldedScalarString

REPO_ROOT = Path(__file__).resolve().parents[2]
GLOSSARY_PATH = REPO_ROOT / "scripts" / "i18n" / "glossary.json"

DEFAULT_BACKEND = os.environ.get("TRANSLATE_BACKEND", "github").lower()
DEFAULT_MODEL_BY_BACKEND = {
    "github": os.environ.get("TRANSLATE_MODEL", "openai/gpt-5-mini"),
    "anthropic": os.environ.get("TRANSLATE_MODEL", "claude-sonnet-4-6"),
}
DEFAULT_ENDPOINT_BY_BACKEND = {
    "github": "https://models.github.ai/inference",
    "anthropic": "https://api.anthropic.com",
}
MAX_RETRIES = int(os.environ.get("TRANSLATE_MAX_RETRIES", "3"))
HTTP_TIMEOUT = httpx.Timeout(connect=10, read=180, write=30, pool=10)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+\S", re.MULTILINE)
LOCALE_HEADER_RE = re.compile(r"^<!--\s*locale:\s*[a-zA-Z-]+\s*-->\s*\n+", re.MULTILINE)


def make_yaml() -> YAML:
    y = YAML()
    y.indent(mapping=2, sequence=4, offset=2)
    y.width = 4096
    y.preserve_quotes = True
    return y


def load_skill(skill_md: Path) -> tuple[Any, str]:
    text = skill_md.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{skill_md}: no frontmatter")
    fm = make_yaml().load(m.group(1))
    return fm, m.group(2)


def dump_skill(fm: Any, body: str) -> str:
    yaml = make_yaml()
    buf = StringIO()
    yaml.dump(fm, buf)
    return f"---\n{buf.getvalue()}---\n\n{body.lstrip()}"


def strip_locale_header(text: str) -> str:
    return LOCALE_HEADER_RE.sub("", text, count=1)


def compute_source_hash(body: str, strings: dict[str, str]) -> str:
    h = hashlib.sha256()
    h.update(body.encode("utf-8"))
    h.update(b"\x00")
    h.update(json.dumps(strings, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    return f"sha256:{h.hexdigest()[:16]}"


def heading_count(text: str) -> int:
    return len(HEADING_RE.findall(text))


def load_glossary() -> dict[str, Any]:
    if not GLOSSARY_PATH.is_file():
        return {"terms": {}, "do_not_translate": []}
    return json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))


# ----------------------------- prompt construction -----------------------------

def build_system_prompt(source_locale: str, target_locale: str, glossary: dict[str, Any]) -> str:
    terms_key = f"{source_locale}_to_{target_locale}"
    terms = glossary.get("terms", {}).get(terms_key, {})
    do_not_translate = glossary.get("do_not_translate", [])

    rules = (
        f"You are a precise technical translator for DesireCore market skill documentation.\n"
        f"Translate from {source_locale} to {target_locale}.\n\n"
        "STRICT RULES:\n"
        "1. Preserve Markdown structure exactly: heading levels, list nesting, tables, blockquotes, "
        "fenced code blocks (```...```), inline code (`...`), HTML tags, SVG, YAML keys.\n"
        "2. NEVER translate: code inside fences, inline `code`, URLs, file paths, command-line args, "
        "env vars (e.g., $FOO, ${BAR}), Python/JS identifiers, YAML/JSON keys, version numbers.\n"
        "3. Preserve exact heading text styling: '# H1', '## H2', etc.\n"
        "4. Preserve list markers: '- ', '* ', '1. '. Preserve checkbox '[ ]' and '[x]'.\n"
        "5. Preserve emoji, ASCII art (e.g. boxed diagrams), tree-view characters (├ └ │ ─).\n"
        "6. Translate body prose, table cells (text only, not code), and short heading words.\n"
        "7. Keep the output length within ~110% of the input length when possible.\n"
        "8. Do NOT add explanatory comments, translator notes, or 'Translated from...' headers.\n"
        "9. The first line may be an HTML comment '<!-- locale: ... -->'. Update its locale code "
        "to the target locale; otherwise leave the comment unchanged.\n"
    )
    glossary_lines = ["GLOSSARY (use these mappings exactly):"]
    for src, tgt in terms.items():
        glossary_lines.append(f"  {src} → {tgt}")
    if do_not_translate:
        glossary_lines.append("\nDO NOT TRANSLATE these brand/technical terms (keep verbatim):")
        glossary_lines.append("  " + ", ".join(do_not_translate))

    output_format = (
        "\n\nRESPONSE FORMAT:\n"
        "Return ONLY a single JSON object with these keys (no preamble, no code fence around the JSON):\n"
        "  - body:        translated Markdown body (string, may contain backticks/fences)\n"
        "  - name:        translated short name (string, ≤100 chars)\n"
        "  - short_desc:  translated short description (string, ≤200 chars)\n"
        "  - description: translated long description (string, ≤2000 chars)\n"
    )

    return rules + "\n" + "\n".join(glossary_lines) + output_format


# ----------------------------- backends -----------------------------

def call_github_models(system_prompt: str, user_payload: str, model: str, endpoint: str) -> str:
    """Call GitHub Models inference API (OpenAI-compatible chat completions).

    Endpoint base: https://models.github.ai/inference
    Auth: Authorization: Bearer <GITHUB_TOKEN>  (token must have `models: read` scope).
    """
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN (or GH_TOKEN) not set. In CI, ensure your job has `permissions: models: read`. "
            "Locally, create a fine-grained PAT with 'Models: Read' permission."
        )
    url = f"{endpoint.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload},
        ],
        "temperature": 0.1,
        "max_tokens": 8192,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    return _post_with_retries(url, headers, payload, extract=_extract_openai_text)


def call_anthropic(system_prompt: str, user_payload: str, model: str, endpoint: str) -> str:
    """Call Anthropic Messages API directly."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    url = f"{endpoint.rstrip('/')}/v1/messages"
    payload = {
        "model": model,
        "max_tokens": 8192,
        "system": [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user_payload}],
        "temperature": 0.1,
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    return _post_with_retries(url, headers, payload, extract=_extract_anthropic_text)


def _extract_openai_text(resp_json: dict) -> str:
    try:
        return resp_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected OpenAI-compatible response shape: {resp_json}") from e


def _extract_anthropic_text(resp_json: dict) -> str:
    try:
        parts = resp_json["content"]
        return "".join(p.get("text", "") for p in parts if p.get("type") == "text")
    except (KeyError, TypeError) as e:
        raise RuntimeError(f"Unexpected Anthropic response shape: {resp_json}") from e


def _post_with_retries(url: str, headers: dict, payload: dict, *, extract) -> str:
    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with httpx.Client(timeout=HTTP_TIMEOUT) as client:
                resp = client.post(url, headers=headers, json=payload)
            # Don't retry on 413: payload won't get smaller on next attempt.
            if resp.status_code == 413:
                raise RuntimeError(
                    f"413 Payload Too Large from {url} — skill body too big for this backend. "
                    f"Switch backend (TRANSLATE_BACKEND=anthropic), use a model with larger input budget, "
                    f"or set translated_by: human to lock the locale."
                )
            if resp.status_code == 429 or resp.status_code >= 500:
                raise httpx.HTTPStatusError(f"{resp.status_code}", request=resp.request, response=resp)
            resp.raise_for_status()
            return extract(resp.json())
        except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError) as e:
            last_err = e
            if attempt < MAX_RETRIES:
                wait = 2 ** attempt
                sys.stderr.write(f"[translate] retry {attempt}/{MAX_RETRIES} after {wait}s ({e})\n")
                time.sleep(wait)
    raise RuntimeError(f"Translation failed after {MAX_RETRIES} attempts: {last_err}")


def call_llm(system_prompt: str, user_payload: str, *, backend: str, model: str, endpoint: str) -> dict[str, str]:
    if backend == "github":
        text = call_github_models(system_prompt, user_payload, model, endpoint)
    elif backend == "anthropic":
        text = call_anthropic(system_prompt, user_payload, model, endpoint)
    else:
        raise RuntimeError(f"Unknown backend: {backend}")
    return parse_json_response(text)


def parse_json_response(text: str) -> dict[str, str]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n", "", text)
        text = re.sub(r"\n```\s*$", "", text)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            obj = json.loads(m.group(0))
        else:
            raise RuntimeError(f"Failed to parse model response as JSON: {e}\n--- Raw response ---\n{text[:500]}")
    for k in ("body", "name", "short_desc"):
        if k not in obj or not isinstance(obj[k], str):
            raise RuntimeError(f"Translation response missing required key '{k}'")
    obj.setdefault("description", "")
    return obj


# ----------------------------- per-skill translation -----------------------------

def translate_skill(
    skill_dir: Path,
    target_locale: str,
    *,
    check_only: bool,
    mark_human: bool,
    backend: str,
    model: str,
    endpoint: str,
) -> dict[str, Any]:
    rel = skill_dir.relative_to(REPO_ROOT).as_posix()
    skill_md = skill_dir / "SKILL.md"
    plan: dict[str, Any] = {"skill": rel, "target": target_locale, "actions": [], "errors": []}

    fm, root_body = load_skill(skill_md)
    metadata = fm.get("metadata") or {}
    i18n = metadata.get("i18n") if isinstance(metadata, dict) else None
    if not isinstance(i18n, dict):
        plan["errors"].append("metadata.i18n missing — run migrate.py first")
        return plan

    source_locale = i18n.get("source_locale")
    default_locale = i18n.get("default_locale")
    if not source_locale or not default_locale:
        plan["errors"].append("i18n missing source_locale or default_locale")
        return plan
    if target_locale == source_locale:
        plan["actions"].append("target == source, skipping")
        return plan

    src_block = i18n.get(source_locale) or {}
    src_body_path_str = src_block.get("body")
    if not src_body_path_str:
        plan["errors"].append(f"i18n.{source_locale}.body not set")
        return plan
    src_body_file = (skill_dir / src_body_path_str.removeprefix("./")).resolve()
    if not src_body_file.is_file():
        plan["errors"].append(f"source body file not found: {src_body_path_str}")
        return plan

    src_body_text = strip_locale_header(src_body_file.read_text(encoding="utf-8"))
    src_strings = {
        "name": str(src_block.get("name", "")),
        "short_desc": str(src_block.get("short_desc", "")),
    }
    if src_block.get("description"):
        src_strings["description"] = str(src_block["description"])
    current_hash = compute_source_hash(src_body_text, src_strings)

    target_block = i18n.get(target_locale) or {}
    if target_block.get("translated_by") == "human":
        if target_block.get("source_hash") != current_hash:
            plan["actions"].append(
                f"WARN: human-translated locale {target_locale} is stale "
                f"(source_hash drift). Skipping; please update manually."
            )
        else:
            plan["actions"].append(f"locale {target_locale} is human-locked, skipping")
        return plan

    needs = (not target_block) or (target_block.get("source_hash") != current_hash)
    if not needs:
        plan["actions"].append(f"locale {target_locale} is up-to-date (hash match), skipping")
        return plan

    if check_only:
        plan["actions"].append(f"locale {target_locale} needs translation (hash mismatch or missing)")
        plan["needs_translation"] = True
        return plan

    payload = {
        "source_locale": source_locale,
        "target_locale": target_locale,
        "skill_id": skill_dir.name,
        "source": {
            "name": src_strings["name"],
            "short_desc": src_strings["short_desc"],
            "description": src_strings.get("description", ""),
            "body": src_body_text,
        },
    }
    user_payload = (
        "Translate the following skill content. Return ONLY the JSON object as specified.\n\n"
        f"```json\n{json.dumps(payload, ensure_ascii=False)}\n```"
    )
    glossary = load_glossary()
    system_prompt = build_system_prompt(source_locale, target_locale, glossary)

    plan["actions"].append(f"calling {backend}/{model} for {target_locale} translation ...")
    translated = call_llm(system_prompt, user_payload, backend=backend, model=model, endpoint=endpoint)

    src_h = heading_count(src_body_text)
    tgt_h = heading_count(translated["body"])
    if abs(tgt_h - src_h) > 0:
        plan["errors"].append(f"heading count mismatch (source={src_h}, target={tgt_h}); rejecting")
        return plan

    if target_locale not in i18n.get("locales", []):
        i18n["locales"].append(target_locale)
    new_block: dict[str, Any] = {
        "name": translated["name"],
        "short_desc": translated["short_desc"],
    }
    if translated.get("description"):
        desc = translated["description"]
        new_block["description"] = FoldedScalarString(desc) if "\n" in desc or len(desc) > 80 else desc
    if target_locale == default_locale:
        new_block["body"] = "./SKILL.md"
    else:
        new_block["body"] = f"./SKILL.{target_locale}.md"
    new_block["source_hash"] = current_hash
    translator_tag = "human" if mark_human else f"ai:{backend}:{model}"
    new_block["translated_by"] = translator_tag
    new_block["translated_at"] = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    i18n[target_locale] = new_block

    body_to_write = translated["body"]
    if target_locale == default_locale:
        body_to_write = LOCALE_HEADER_RE.sub("", body_to_write, count=1)
        skill_md.write_text(dump_skill(fm, body_to_write), encoding="utf-8")
        plan["actions"].append(f"wrote root SKILL.md with translated body ({len(body_to_write)} chars)")
    else:
        target_body_file = skill_dir / f"SKILL.{target_locale}.md"
        if not body_to_write.startswith("<!-- locale:"):
            body_to_write = f"<!-- locale: {target_locale} -->\n\n{body_to_write.lstrip()}"
        target_body_file.write_text(body_to_write, encoding="utf-8")
        skill_md.write_text(dump_skill(fm, root_body), encoding="utf-8")
        plan["actions"].append(f"wrote {target_body_file.name} ({len(body_to_write)} chars) and updated root frontmatter")

    return plan


def get_target_locales(args: argparse.Namespace) -> list[str]:
    if args.target:
        return [args.target]
    manifest_path = REPO_ROOT / "manifest.json"
    if not manifest_path.is_file():
        return ["en-US"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["en-US"]
    return list(manifest.get("supportedLocales") or ["en-US"])


def resolve_backend(args: argparse.Namespace) -> tuple[str, str, str]:
    backend = (args.backend or DEFAULT_BACKEND).lower()
    if backend not in ("github", "anthropic"):
        raise SystemExit(f"Unknown backend '{backend}'; choose 'github' or 'anthropic'")
    model = args.model or DEFAULT_MODEL_BY_BACKEND[backend]
    endpoint = args.endpoint or os.environ.get("TRANSLATE_ENDPOINT") or DEFAULT_ENDPOINT_BY_BACKEND[backend]
    return backend, model, endpoint


def list_github_models() -> int:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.stderr.write("ERROR: GITHUB_TOKEN/GH_TOKEN not set\n")
        return 2
    url = "https://models.github.ai/catalog/models"
    with httpx.Client(timeout=HTTP_TIMEOUT) as c:
        resp = c.get(url, headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    for m in resp.json():
        print(f"  {m.get('id',''):50s} {m.get('publisher','')}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Skill directories (default: all under skills/)")
    parser.add_argument("--target", help="Single target locale (default: all manifest.supportedLocales)")
    parser.add_argument("--check", action="store_true", help="Report stale translations; exit 1 if any")
    parser.add_argument("--human", action="store_true", help="Mark new translations as 'human' (locks against re-translation)")
    parser.add_argument("--backend", choices=("github", "anthropic"), help="Override backend (default: env TRANSLATE_BACKEND or 'github')")
    parser.add_argument("--model", help="Override model id")
    parser.add_argument("--endpoint", help="Override API endpoint")
    parser.add_argument("--list-models", action="store_true", help="List models in GitHub Models catalog and exit")
    args = parser.parse_args(argv)

    if args.list_models:
        return list_github_models()

    backend, model, endpoint = resolve_backend(args)

    if not args.check:
        if backend == "github" and not (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")):
            sys.stderr.write("ERROR: GITHUB_TOKEN (or GH_TOKEN) not set for backend='github'\n")
            return 2
        if backend == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
            sys.stderr.write("ERROR: ANTHROPIC_API_KEY not set for backend='anthropic'\n")
            return 2

    if args.paths:
        targets = [Path(p).resolve() for p in args.paths]
    else:
        targets = sorted((REPO_ROOT / "skills").iterdir())
        targets = [t for t in targets if t.is_dir() and (t / "SKILL.md").is_file()]

    target_locales = get_target_locales(args)

    plans: list[dict[str, Any]] = []
    for skill_dir in targets:
        if not (skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file()):
            continue
        for tl in target_locales:
            try:
                plans.append(translate_skill(
                    skill_dir, tl,
                    check_only=args.check, mark_human=args.human,
                    backend=backend, model=model, endpoint=endpoint,
                ))
            except Exception as e:  # don't let one bad skill abort the entire run
                plans.append({
                    "skill": skill_dir.name,
                    "target": tl,
                    "actions": [],
                    "errors": [f"unhandled exception: {e}"],
                })

    needs = [p for p in plans if p.get("needs_translation")]
    errs = [p for p in plans if p.get("errors")]
    if args.check:
        for p in plans:
            for a in p["actions"]:
                print(f"  [{p['skill']}/{p['target']}] {a}")
        for p in errs:
            for e in p["errors"]:
                print(f"  ERROR [{p['skill']}/{p['target']}]: {e}")
        return 1 if needs else 0

    print(f"Backend: {backend}  Model: {model}  Endpoint: {endpoint}\n")
    for p in plans:
        print(f"{p['skill']} → {p['target']}:")
        for a in p["actions"]:
            print(f"  - {a}")
        for e in p.get("errors", []):
            print(f"  ✗ ERROR: {e}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
