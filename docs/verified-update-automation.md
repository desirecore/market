# Verified upstream updates

This is update automation, not automatic first admission, runtime acceptance or a
security certification. The issue tracker remains enabled and is independent of
admission evidence. No credentials, private feeds or user tokens belong here.

## Trusted inputs and scope

* The daily upstream-health job still checks Git pointers. The Git proposer uses
  exact old/new SHA, the existing delta auditor and the old admitted evidence.
* `config/verified-updates.v1.json` adds explicit tracking for non-pointer/local
  sources. Currently registered: the owner-qualified ClawHub AMap package and
  the local AI News Radar edition. No unregistered source is guessed.
* `clawhub` verifies the registered owner, gets an explicit stable latest version,
  downloads its version-specific ZIP and verifies the old pinned digest again.
  Registry MIT-0 metadata is **not** permission to override package MIT evidence.
* `github-file` resolves a configured repository/branch/path to an immutable
  commit, then retrieves that exact raw file. This is the Web discovery adapter.
* `github-release` selects one explicitly configured asset from an actual stable
  GitHub release, never an inferred version string. Mutable assets whose old
  bytes no longer match the admitted digest are blocked.
* Automatic artifact auditing currently supports root-layout packages. A nested
  install scope needs an explicitly reviewed layout adapter. Arbitrary hosts,
  symlinks, executable ZIP entries, path traversal, duplicate/case-colliding
  names, encrypted archives and over-budget artifacts fail closed.
* A new hash is identification only. Old/new bytes undergo the existing license,
  notice, dependency, frontmatter and metadata delta audit. Receipts name the
  actual SHA-256/upstream SHA; temporary Git objects only transport comparisons.

For a new Web source, add a reviewed tracking entry such as:

```json
{"adapter":"github-file","repo":"example/project","branch":"main","path":"SKILL.md"}
```

A release ZIP uses `adapter: github-release`, `repo`, and an exact `asset` name.
The old market pointer/digest/admission must already be valid. These examples do
not enable first-time installs or authorize any unreviewed source.

## Local editions

The local-git map records the exact upstream SHA, upstream path/hash, installed
path/hash/mode, and every market-only wrapper. No newly discovered files are
silently imported. Missing/moved files, added upstream license/notice obligations,
changed permissions and mapping drift block advancement. Unmodified imported
files can be replaced; a file changed by both upstream and market is a conflict,
never a blind overwrite. Market wrappers/translations remain intact.

AI News Radar tracks the actual upstream `master` branch. Its existing generator
and the five previously reported alerts are not changed by this tooling PR.
Real read-only discovery currently detects a conflict in locally transformed
reference documentation; the safe result is a draft/manual reconciliation, not
an overwritten wrapper or a claim that the newer upstream already passed.

## Publication and merge authority

Both publishers verify `gh api user` is `mashagua`; published commits use the
maintainer's designated identity. Configure an appropriately scoped maintainer
credential as the Actions secret `MARKET_MAINTAINER_TOKEN` through approved secret
management. This change neither creates nor reads credential values. With no
credential the workflows run audit/verification only; there is no bot-identity
fallback. Checkout credentials are not persisted; publishing uses an ephemeral
git credential helper environment. The issue-reporting step retains the normal
workflow token and its existing behavior.

The merge workflow runs after validation-related workflow completions, hourly
at minute 47, and manually. It only checks out **current main**, not PR files or
workflow artifacts; it never runs PR/upstream code. Labels and PR JSON are not
trust roots. For each same-repository maintainer update PR it:

1. Independently rediscovers/re-fetches the target and recomputes the complete
   allowed proposal using trusted-main policy and special-review records.
2. Requires the complete PR diff to equal that result. Tooling/workflow changes,
   changed review exceptions, foreign paths or forged receipts cannot enter.
3. Conservatively permits automatic merge only when the **installed payload is
   byte/mode-identical**. Real content/behavior changes still need human review.
   Passing structural metadata checks alone cannot prove permissions unchanged.
4. Requires all applicable check/context results complete and successful on the
   exact final head, including validate, translate, CodeQL/Analyze and Copilot
   wait; outstanding changes-requested reviews block. No ignored CodeQL failures.
5. Requires current-base ancestry, a clean server state, and active strict
   server-side up-to-date rules for validate/translate to close the base race.
   The merge API binds the expected head SHA, uses squash, and has no bypass.
6. Merges at most one PR per run, then stops because main has advanced. Behind
   branches remain held for a normal merge update and new final-head checks.

Thus this does **not** promise autonomous merging of arbitrary changed skill
scripts/prompts. Such a broader behavioral/permission approval policy has not
been established. This mechanism PR itself is outside the allowed diff and must
be reviewed/merged separately by a maintainer.

Daily discovery remains 09:23 Asia/Singapore (GitHub can delay execution). Git
and configured-source publishers each have a five-candidate cap. An existing
open PR for a skill is preserved, not overwritten; the same closed candidate is
not recreated. Discovery/audit/validation failures retain old admission and
become drafts/manual findings. Nothing automatically promotes listing-only.

## Offline checks

```sh
uv run scripts/catalog/validate_catalog_metadata.py --require-complete
uv run scripts/i18n/validate-i18n.py
uv run scripts/i18n/translate.py --check
uv run --with pytest --with jsonschema --with pyyaml --with 'lxml>=5.3,<7' --with 'defusedxml>=0.7' python -m pytest scripts
```

`uv run scripts/catalog/publish_tracked_updates.py` performs real discovery and
audit planning without publication. `merge_verified_updates.py` defaults to
verification-only and must run from current main; `--merge` additionally requires
the maintainer credential and every gate above. Do not run publishing/merge flags
as a smoke test against real PRs.
