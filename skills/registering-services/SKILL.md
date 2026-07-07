---
name: registering-services
description: >-
  Register an external HTTP/MCP service to the global Application & Service
  Catalog so that other Agents (and the human user) can discover and call it.
  Use when the user mentions adding a new service, registering an API, or
  publishing a backend you control to the team's catalog. 新增服务、注册 API、把后端发布到团队目录时使用。
version: 1.0.1
type: meta
risk_level: medium
status: enabled
disable-model-invocation: true
tags:
  - service
  - registration
  - catalog
  - meta
metadata:
  author: desirecore
  updated_at: '2026-06-29'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 注册服务
      short_desc: 把外部 HTTP/MCP 服务登记到全局应用与服务目录
      description: >-
        把外部 HTTP/MCP 服务登记到全局应用与服务目录，让其他 Agent 与人类用户都能发现并调用。
        Use when 用户提到要新增服务、注册 API 或把你掌握的后端发布到团队目录。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: Register Services
      short_desc: Register external HTTP/MCP services into the global catalog
      description: >-
        Register an external HTTP/MCP service to the global Application & Service Catalog so that other Agents (and the human user) can discover and call it. Use when the user mentions adding a new service, registering an API, or publishing a backend you control to the team's catalog.
      body: ./SKILL.md
      translated_by: human
      source_hash: sha256:dcd8732ac76f009f
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#34C759" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="12" height="6" rx="1.5"/><rect x="3" y="14" width="12" height="6" rx="1.5"/><circle cx="6.5" cy="7" r="0.5" fill="#34C759"/><circle cx="6.5" cy="17" r="0.5" fill="#34C759"/><line x1="19.5" y1="5" x2="19.5" y2="11"/><line x1="16.5" y1="8" x2="22.5" y2="8"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# registering-services Skill

## L0: One-line Summary

Tell the Agent how to register an external HTTP/MCP service into the global
catalog with human governance.

## L1: Overview

This meta-skill teaches you (the Agent) **how** to add a new service to the
shared "Apps & Services" catalog. It does **not** invoke external services
itself — once registered, use the per-service Skill at `~/.desirecore/skills/svc-<id>/`
or the `using-services` meta-skill to actually call them.

### When to use this skill

- The user asks to register an API or service (e.g. "add the Acme search
  endpoint to our catalog")
- You just deployed a backend you want other Agents to be able to reach
- You discover a useful public API and want to make it shareable

### When NOT to use it

- One-off HTTP calls that nobody else needs to repeat — just call `HttpRequest`
  directly
- Adding an MCP server to **your own** agent only — POST to
  `/api/agents/<your-id>/mcp-servers` instead, no catalog entry needed
- Modifying an existing catalog entry — the user must promote/reject through
  the Store UI

## L2: How to register a service

### Step 1 — Gather the required fields

Before calling the API, collect:

| Field | Required | Notes |
|------|----------|-------|
| `id` | yes | kebab-case, globally unique (e.g. `acme-search-api`) |
| `name` | yes | Human-readable display name |
| `description` | yes | One sentence — what it does |
| `protocol` | yes | `'http'` or `'mcp'` |
| `tags` | yes | Searchable list, e.g. `['search', 'web']` |
| `registeredBy` | yes | **Your own agent id** |
| `endpoint` | **required when `protocol='http'`** | Base URL of the API |
| `riskLevel` | recommended | `low` / `medium` / `high` / `critical` |
| `auth` | when API requires auth | `{ type, secretRef }` — see below |
| `operations` | recommended | Operations list for the per-service Skill |
| `capabilities` | optional | What this service can do |

### Step 2 — Choose `riskLevel` honestly

`riskLevel` decides whether **future calls** to this service trigger an
approval gate:

- `low` — read-only data that's safe to invoke without prompting (e.g. public weather API)
- `medium` — default for most APIs; first invoke per session may prompt
- `high` — services that move money, send emails, mutate user data
- `critical` — services that can cause irreversible harm; **every** call requires human approval

**Bias toward higher risk if uncertain.** Under-classifying is worse than over-classifying.

### Step 3 — Reference credentials with `secretRef`, never inline

**Do not put API keys/tokens into the catalog entry.** The catalog is global,
visible in the Store UI, and may be inspected by future people. Instead:

```jsonc
{
  "auth": {
    "type": "bearer",
    "secretRef": "secrets/api-keys/acme"  // pointer, not the actual key
  }
}
```

`HttpRequest` resolves `secretRef` at call time. If the secret doesn't exist
yet, ask the user to provide it through their own secrets manager — not
through the chat.

### Step 4 — Call the registration API

Use the `HttpRequest` tool to POST to the local Agent Service:

```yaml
tool: HttpRequest
parameters:
  url: http://127.0.0.1:<agent-service-port>/api/registry/agent-services
  method: POST
  body:
    id: acme-search-api
    name: "Acme Search API"
    description: "Full-text search across Acme's product catalog"
    protocol: http
    endpoint: https://api.acme.example/search
    tags: ["search", "products"]
    registeredBy: "<your-agent-id>"
    riskLevel: medium
    auth:
      type: bearer
      secretRef: secrets/api-keys/acme
    operations:
      - name: search
        method: GET
        path: /v1/items
        description: "Search products by query string"
      - name: getDetail
        method: GET
        path: /v1/items/{id}
        description: "Get a single product by id"
```

(The Agent Service port is available via the runtime; ask `request-help`
skill if you're unsure how to discover it.)

### Step 5 — Wait for human approval

The endpoint triggers a **service-approval** request to the human user. The
HTTP call will block until they approve or reject through the Store UI.

- **Approved** → entry is written to
  `~/.desirecore/config/registry-agent-services.json` with
  `reviewStatus: 'pending'`. While `pending`, **only you** (the registering
  Agent) can call it.
- **Rejected** → the API returns 403; do not retry, ask the user how to
  proceed.

After approval, the human can later **promote** the entry from `pending` to
`approved` in the Store UI. Promotion makes the service callable by all
Agents and triggers `service-skill-generator` to write
`~/.desirecore/skills/svc-<id>/SKILL.md` with concrete examples derived
from the `operations` you provided.

### Step 6 — Don't re-register

If `POST /api/registry/agent-services` returns `409 Conflict`, the service
already exists. Do not try alternative ids unless the user explicitly asks
you to register a separate variant — silently shadowing an existing service
is a governance failure.

## Failure modes

- **Endpoint blocked by SSRF guard**: the registration API rejects private
  network addresses (10.x / 172.16-31.x / 192.168.x / 169.254.x) except
  localhost. Public IPs and DNS names are allowed.
- **Missing `registeredBy`**: the API returns 400. Always include your own
  agent id — there is no anonymous registration.
- **Approval timeout**: the broker times out after the user is idle long
  enough; treat this as `rejected`.
