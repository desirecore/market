# Third-Party Notices

This repository's own content (DesireCore-authored skills and metadata) is licensed
under the MIT License (see `LICENSE`). Some bundled skills are derived from or
authored by third parties and are governed by their own terms, noted below. The
`license` / `redistribution` fields on each entry are the source of truth per skill.

## Anthropic skills (`anthropics/skills`)

The following skills are **source-available, NOT open source**. Per Anthropic's
`anthropics/skills` README they are provided for demonstration and educational
purposes only. They are included here as reference implementations; verify
Anthropic's terms before redistribution or production use.

- `skills/docx`
- `skills/pdf`
- `skills/pptx`
- `skills/xlsx`

Other Anthropic-authored skills in this repository are licensed under
**Apache-2.0** (e.g. `skills/frontend-design`); the Apache-2.0 license and any
required NOTICE attribution apply to those skills.

Upstream: https://github.com/anthropics/skills

## External / pointer skills

Skills described only by an `entry.json` pointer (no vendored source) are
maintained by their respective upstreams and governed by each upstream's license.
See the `license` and `redistribution` fields in each `skills/<id>/entry.json`.
Entries with `redistribution: source-pointer-only` or `verify-package-terms` are
not redistributed here; their content is fetched from the upstream at install time.
