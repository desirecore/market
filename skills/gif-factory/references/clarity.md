# Fixing blurry photographic stickers

Use this guide for realistic people, photographic pets, detailed illustrations, or a user report that a face looks blurry. Choose intentional pixel art when the user asks for that appearance; do not apply a photographic treatment to every pack.

## Diagnose before regenerating

Compare the original transparent sprite crop with a frame decoded from the exported GIF, at the same display size. Also inspect the decoded MP4. This separates source softness, compositor pixelation and playback scaling.

In explicit `--render-style pixel` mode, `export_pack.py` deliberately resizes a sprite to about 106 pixels high, places it on a 160 × 160 canvas, then enlarges the composite to 320 × 320 with nearest-neighbor sampling. This makes a pixel-style sticker, but discards facial detail from a photographic source. Enlarging that result or changing only the final output dimensions cannot recover the discarded detail.

If the original crop is already soft or the face occupies very few source pixels, obtain a clearer reference or regenerate the pose with the face larger. Do not promise that resizing can restore missing detail or identity.

## Built-in HD export (default)

Run the ordinary export command; no extra flag or compositor edit is needed:

```sh
python3 scripts/export_pack.py manifest.json build --font /path/to/font.ttf --preview
```

The default is `hd` and 512 × 512, including when an older manifest has no rendering field. A manifest can explicitly choose `"render_style": "hd"` or `"render_style": "pixel"`; `--render-style hd` or `--render-style pixel` overrides it. Choose pixel only when that appearance is intended. Do not use image-content heuristics to silently switch a face to pixel mode.

HD previews use a clean grid at native GIF resolution, with no title overlay by default. Use `--preview-layout chapters` if category headings are wanted; `--preview-layout clean` also works with pixel exports. The offline gallery uses normal image sampling for HD and pixel sampling for pixel art.

## How the HD path preserves detail

The bundled HD implementation follows this tested recipe:

1. Start every animation frame from the original high-resolution atlas crop. Respect the accepted cell/crop boundaries. Crop to the meaningful alpha bounds; discard low-alpha generation noise before fitting the sprite.
2. Compose directly at the final GIF resolution. The HD output is **512 × 512**, rather than a 160-pixel intermediate canvas. Fit the sprite within roughly **400 pixels wide and 330 pixels high**, with its resting bottom around **y=390**, leaving space for the caption and motion. These bounds are starting values, not requirements for every pose.
3. Resize the original sprite with **LANCZOS** for each frame. Use **BICUBIC** sampling for continuous affine/shear deformation. Avoid nearest-neighbor sampling and coarse horizontal strip deformation on faces. Retain pixel sampling on decorative pixel icons only when that look is intentional.
4. Scale the existing motion offsets from their 160-unit design space to the final canvas (`final_size / 160`). Include the full jump, squash and shear in the safe-margin calculation. Add transparent padding around transformed sprites so the deformation cannot clip them. If a motion reaches the edge, reduce sprite occupancy or motion amplitude and re-export.
5. Render captions and outlines at the final size. Keep approved text and facial expression. In the tested 512-pixel composition, captions were centered near y=450 with a font around 56–62 pixels. Fit longer captions to the available width.
6. Quantize the finished frames to a shared GIF palette, reserve a transparent index and use disposal mode 2. Smooth edges can be rasterized once at final resolution; avoid repeating alpha thresholding and enlargement. GIF has a limited palette and binary transparency, so check skin gradients and edges on a contrasting background.
7. Preserve the intended timing; the existing pack uses 24 samples × 80 ms = **1.92 seconds**, looping indefinitely. Adjacent identical frames may be merged by the encoder without changing total duration.

## Validate the delivered result

- Decode each final GIF and check actual dimensions, loop flag, total duration, transparency, distinct visible frames and safe margins throughout the loop.
- Assemble the MP4 preview from decoded final GIF frames. Use smooth scaling when needed, and avoid enlarging a low-resolution preview as the quality check. Respect the user's choice about titles and labels.
- Compare the previous GIF and new GIF at the **same display size**, using comparable animation phases. Inspect eyes, glasses, hair, skin and clothing texture. Make clear when a comparison is a static image.
- Verify the ZIP contents and MP4 decoding. Higher-resolution photographic GIFs can be larger; report size or platform limits when they affect the requested use. Do not claim messaging-platform compatibility from local playback alone.

The demonstrated correction rebuilt four photographic public-figure stickers from the same source art at 512 × 512. Face and clothing detail improved after removing the pixel intermediate. That is evidence for fixing this rendering failure, not a guarantee that every source image can be made sharp.
