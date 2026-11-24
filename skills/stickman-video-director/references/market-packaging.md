# Market package notes and on-demand assets

This optional local package is taken from `kaomei/stickman-video-director@10287822ba47579321068da1b93801face9160dd` path `skills/directing-stickman-videos`, plus the repository-root MIT LICENSE.

The installer copies only the selected content directory, so LICENSE is placed in this package. The catalog slug is `stickman-video-director`; the upstream frontmatter name was `directing-stickman-videos`.

## What is already in the package

Scripts, references, font files and their OFL licenses, audio-library catalog/INDEX/licenses/CREDITS/evidence, A-mode and B1–B7 style boards and approved stills that fit the slim package, B6 character/starter/production descriptors, and `package.json` / lockfile. Node.js 20+ and the declared npm dependencies (`@napi-rs/canvas`, `sharp`) are required for the local Code Engine renderer; they are not bundled as binaries. Some B-mode scripts also use Python. See `package.json` and `scripts/requirements-b8.txt`.

## What you must fetch explicitly before some B-mode work

These groups are runtime-necessary for the named modes but are too large to vendor in the market repository. They are **not** installed automatically.

- `required-for-B-audio` — `assets/b-audio-library/audio/*` soundtrack binaries (about 248 MiB).
- `required-before-B6` — `assets/b6/reference/*` style-lock videos, including the stated Eiffel V44 standard (about 50.6 MiB).
- `required-for-B6-paint` — `assets/b6/paint/*` default paint-kit plates (about 13.9 MiB).
- `required-before-B8` — approved B8 default visual references and the portable midas replay pack (about 57.5 MiB).

Run, from a working copy of this skill:

```bash
python3 scripts/fetch-optional-assets.py \
  --manifest references/fetch-manifest.json \
  --dest /absolute/path/outside-the-skill \
  --group required-for-B-audio
```

Repeat or omit `--group` for the other groups. The script only downloads the pin-fixed raw.githubusercontent.com URLs in the manifest and verifies SHA-256. It does not execute downloads. After verification, copy or symlink the resulting `assets/...` tree into the installed skill so the original relative paths resolve.

## What was excluded as example or QA output

Repository README demo media, skill `examples/`, `public-showcases`, B5 `local-baselines` / example trees / approved-sample.mp4, and B6 `hong-kong-v90` work-in-progress example productions. Those remain at the pin.
