# Pixel full-character actions

Use this route for intentional pixel art that performs a complete action. Keep it distinct from pixel light motion (`export_pack.py --render-style pixel`) and smooth HD actions (`export_keyframes.py`). The user accepted the exact [four-character, twenty-GIF pack](../examples/pixel-actions/production.json); new outputs still require inspection.

## Identity and acting

Start from the accepted pixel character reference, including head/body proportions, palette, outline weight and accessories. For a requested style conversion, establish the pixel identity before expanding. Glasses, hood, helmet and scarf are identity anchors in this pack, not mandatory accessories for other characters.

Generate one transparent action atlas per GIF, usually sixteen consecutive poses in a 4 × 4 sheet. Keep lettering out. Plan neutral → anticipation → gesture → recovery → settling; the final pose should lead naturally into the first. Sixteen drawings at 120ms (1.92 seconds) is the accepted example's timing, not a universal smoothness threshold.

Coordinate head, expression, shoulders, torso and relevant limbs. Let hair/clothes/accessories follow. For example: fist-pump with a knee lift; curtsy with a cape following; crouch, hop and land; weight-shifting dance with a trailing scarf. A frozen body with only an arm rotating does not fulfill this route. Each new caption should have a meaningfully different action.

Maintain deliberate square pixel clusters, stepped dark outlines and a consistent limited palette. Don't produce smooth artwork and describe a blurry reduction as pixel design. Review identity/pose anchors before filling transitions on new or unstable characters. For an expansion already authorized by an accepted sample, reuse its chosen appearance, motion and character reference.

## Extraction and composition

Inspect the actual sheet: occupied cells, complete silhouettes, gutters and row breaks. Generated sheets can have outer margins that shift every column away from the nominal grid. Compare stable landmarks across multiple rows before applying **fixed column offsets**. Do not estimate corrections independently from each pose's changing hand or silhouette bounds; that can erase intended movement.

`export_pixel_actions.py` takes one shared union crop and scale for the full action, composes on a 160px logical canvas and doubles to 320px with nearest-neighbor sampling. It uses a shared GIF palette and a still caption. No smooth resampling, crossfades or whole-sprite warping are added. Source alpha below 144 is discarded to remove nearly transparent export noise; inspect fine details after this threshold. Regenerate baked-in backgrounds or clipped anatomy instead of relying on this threshold to repair them.

```json
{
  "entries": [{
    "name": "boy-thumbs-up",
    "text": "点赞",
    "atlas": "poses.png",
    "grid": [4, 4],
    "column_offsets": [0, 0, 0, 0]
  }]
}
```

Paths are relative to the manifest. Without `frames`, all cells play in reading order at 120ms. Optional `frames` selects cells and timing, for example `[{"cell":[0,0],"duration":120},{"cell":[1,0],"duration":120}]`. Durations must be positive multiples of 10ms. `column_offsets` moves a whole column's sprites left by the specified source pixels; zero is the default. Use offsets only after checking the actual layout. All entries need unique output names; captions may repeat across different characters.

```sh
python3 scripts/export_pixel_actions.py examples/pixel-actions/action-example.json build-pixel --font /path/to/chinese-font.ttf
python3 scripts/review_gif.py extract build-pixel/boy-thumbs-up.gif build-pixel/review --focus 80 20 240 190
```

The sample atlas is included so this route can be reproduced. Original private references and other generated atlases are not bundled in the public download.

## Review and expansion

Follow [stability.md](stability.md): inspect decoded frames, native-size face/accessories, normal playback and the loop seam. Missing transitions, uneven holds and repeated row-boundary jumps can create 抽帧感. Fix the poses or extraction; increasing FPS, duplicating images or crossfading does not add missing acting. A shared palette and sixteen distinct frames alone do not prove a good action.

The exporter reports technical verification with visual/user acceptance pending. Record an assistant review only after doing it; record user acceptance only for the revision actually accepted. When expanding “each character to five,” preserve the existing accepted GIF and add four actions, keeping five total per character unless the user asks for five additional ones.

Publish accepted examples under appearance + movement, then character, with default-collapsed README galleries. Keep prior light-motion series and pending repair candidates separately labeled. Share standalone GIFs, category folders and a verified ZIP; don't include private photo originals or local filesystem paths in public records.
