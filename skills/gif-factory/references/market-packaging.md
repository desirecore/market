# Market package notes

This optional local package is taken from `WoYun520/gif-factory@e89003a4a6ca4fd0e9e39c8859851b58c82bc368`.

Kept: root and companion skill scripts, fonts, templates, references, style descriptors, the 100 article-cover color cards, paper-mechanism visual references, and LICENSE files.

Not shipped: `examples/`, `docs/` previews, `GALLERY.md`, tests, and rendered PNG/JPG/GIF/MP4/ZIP catalogs under companion `assets/` (style-catalog, english-title previews, signature media, film-title examples).

Those excluded files remain available at the pinned upstream commit. Common sticker export needs Python 3 and Pillow in a private environment. `export_pack.py` / `export_keyframes.py` do not need FFmpeg unless you pass `--preview` to make an MP4. This package does not bundle a generative model or a paid service. The optional external `lemo-opuscar` skill mentioned by the paper-mechanism branch is not included and must be installed separately if you use that workflow.
