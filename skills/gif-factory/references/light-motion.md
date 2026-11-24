# Light-motion stickers

Use when the user wants a small animated beat around a distinct expression/pose: nod, bounce, sway, squash, shake, or floating accents. This is a different method from a gesture unfolding through newly drawn poses.

## Plan and preserve the appearance

- Give every entry a chat line, visibly distinct expression/pose and compatible motion/accent. A new caption or random preset applied to the same portrait is not a new expression. For an existing accepted sample expanded to a pack, preserve its appearance and motion intensity unless asked to change them.
- Generate new pose art with the image tool using the selected appearance guide. A 4×4 atlas can hold different stickers here; it does not necessarily hold sixteen frames of one action. Map actual occupied cells and caption/pose meaning before exporting.
- If the user supplies a finished PNG and wants its current artwork retained, animate that supplied art without unnecessary regeneration. Keep an existing caption separate and fixed; do not squash, nod or shake the entire picture including text.
- Inspect actual alpha. A transparent viewer may look black; hidden RGB speckles with almost-zero alpha are not an opaque backdrop. Do not key out all ivory/white pixels to remove a matte when the costume contains those colors. If a background is baked in, restore transparency with an image edit and recheck.

## Compose

Use [export_pack.py](../scripts/export_pack.py) and [the manifest format](manifest.md). Choose `hd` for clean illustration/photographic work and `pixel` for intentional pixel art. Its `frames` are preset samples of one sprite, not a sequence of generated joint poses. Use [keyframes.md](keyframes.md) when the actual gesture must unfold over time.

```sh
python3 scripts/export_pack.py manifest.json build --font /path/to/font.ttf --preview
# Intentional pixel path:
python3 scripts/export_pack.py manifest.json pixel-build --font /path/to/font.ttf --render-style pixel --preview
```

Keep the original crop for HD sampling. Do not introduce a tiny pixel intermediate for a detailed face. For pixel mode, preserve crisp stepped contours with nearest-neighbor sampling. Match amplitude to the character: a long detailed dress may need a gentler squash than a round cartoon creature. A thankful pose can use a small nod; a celebration can bounce. Avoid increasing deformation just to increase unique-frame counts.

## Review

Inspect the final decoded GIF, not only the initial artwork. Check likeness/style, pose/caption agreement, readable fixed text, motion strength, safe margins, effect overlap, transparency and the loop seam. Check representative playback for every motion family in a pack. If a defect is reported, inspect the affected GIF's individual frames using [review_gif.py](../scripts/review_gif.py); its technical measurements do not decide aesthetic acceptance.

Deliver independent looping GIFs, the pack ZIP and a preview built from those actual GIFs. Keep technical validation, assistant review and user acceptance distinct. Do not advertise a light-motion pose as a newly drawn complete gesture, or silently switch a failed full-action request to this method.
