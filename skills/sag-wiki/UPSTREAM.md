# Upstream provenance and local edition

Source: https://github.com/Zleap-AI/SAG-Wiki/tree/b6940ac834b3b1ec651c0b49dc1b0c45d4d74c4a/cli/skills/sag
Immutable source commit: `b6940ac834b3b1ec651c0b49dc1b0c45d4d74c4a`. Local packaging version: `2026.11.24` (not an upstream release).

Copyright of the upstream skill and LICENSE remains with the upstream authors. The upstream MIT LICENSE is preserved verbatim in this package.

## Changes and exclusions

- Copied cli/skills/sag skill files and the repository-root MIT LICENSE into this market-local optional package so the installed contentDir contains the license text. The DesireCore installer copies only the selected content directory and does not automatically attach a parent LICENSE.
- Added bilingual market SKILL/README-style instructions and this provenance file. The verbatim upstream SKILL.md is kept at references/upstream-skill.md. The catalog slug is sag-wiki; the upstream frontmatter name was sag.
- The rest of the SAG-Wiki application tree, demo videos and third-party binaries are excluded because they are not this skill.

## Imported source manifest

| Upstream path | Package path | Source bytes | Source SHA-256 | Changes |
|---|---|---:|---|---|
| LICENSE | LICENSE | 1073 | 735a34d013f65abea13a18ded72eda3362156cdab391fe3e48649730b3aafa2c | none; copied into the package root so the installer contentDir contains it |
| cli/skills/sag/references/ignores.md | references/ignores.md | 3244 | 9c7dba36a70c4f8ded7bc19ea91eeb6c1682b0a88b77ed6e671eeb414761e3f1 | none |
| cli/skills/sag/references/parameters.md | references/parameters.md | 7885 | 2da7f06f314a2087492d8441fe1c4dbfacca58a58bd06fe4351dc7b373e813e9 | none |
| cli/skills/sag/references/setup.md | references/setup.md | 18502 | 70bfea031a21d27ec352e93ea3c36978a63535cf9b8cd94bc7aac14bb723fefc | none |
| cli/skills/sag/SKILL.md | references/upstream-skill.md | 4996 | 15b8420b09b667b347e3d437f8c08df1f5f114a4d532e853793562e198be80dd | verbatim copy of the upstream skill body, kept for provenance; market package uses slug sag-wiki |

## Excluded from this package

| Upstream path | Bytes | Git blob SHA-1 | Reason |
|---|---:|---|---|

The remainder of the SAG-Wiki repository outside `cli/skills/sag` and the root LICENSE (application code, demo videos, third-party binaries) is excluded as not part of this skill.
