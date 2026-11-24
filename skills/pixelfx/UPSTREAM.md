# Upstream provenance and local edition

Source: https://github.com/patch-gg/pixelfx/tree/5294518ce7c72e48b6100a744596e0acf57f2826/skills/pixelfx
Immutable source commit: `5294518ce7c72e48b6100a744596e0acf57f2826`. Local packaging version: `2026.11.24` (not an upstream release).

Copyright of the upstream skill, LICENSE and NOTICE.md remains with the upstream authors. Both license files are preserved verbatim.

## Changes and exclusions

- Copied skills/pixelfx/SKILL.md plus the repository-root MIT LICENSE and NOTICE.md into this market-local optional package so the installed contentDir contains the license evidence. The DesireCore installer copies only the selected content directory.
- Added bilingual package instructions and this provenance file. The verbatim upstream skill is at references/upstream-skill.md.
- The effect library, Node tools, gallery/fonts (not covered by the repo MIT license) and optional remote pch installer are not vendored. The skill discloses the separate checkout and the need to review any remote install script; this package does not run that script.

## Imported source manifest

| Upstream path | Package path | Source bytes | Source SHA-256 | Changes |
|---|---|---:|---|---|
| LICENSE | LICENSE | 1093 | 0a77565a50c3462831244452f129c38d2adc4fd07897cbeba8adc943f958604e | none; copied into the package root so the installer contentDir contains it |
| NOTICE.md | NOTICE.md | 620 | d12932473f98b1a3f0b5820ae23d568b52e39294ba7c2d60c0649a93a808af3b | none; copied into the package root so the installer contentDir contains it |
| skills/pixelfx/SKILL.md | references/upstream-skill.md | 12121 | b8210917cf4218fbc7d64a07ec4eed4b7888981df3a0224a4681f3547e0f09c5 | verbatim upstream skill text |

## Excluded from this package

| Upstream path | Bytes | Git blob SHA-1 | Reason |
|---|---:|---|---|
