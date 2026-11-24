#!/usr/bin/env python3
"""Compose generated pixel poses using one crop/scale and nearest sampling."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageSequence
import export_pack as pack


def render(entry, base, output, font):
    atlas = Image.open(base / entry['atlas']).convert('RGBA')
    cols, rows = entry.get('grid', [4, 4])
    if cols < 1 or rows < 1:
        raise ValueError('Grid dimensions must be positive')
    offsets = entry.get('column_offsets', [0] * cols)
    if len(offsets) != cols:
        raise ValueError('One fixed offset is required per column')
    frames_spec = entry.get('frames', [{'cell': [c, r], 'duration': 120}
                                      for r in range(rows) for c in range(cols)])
    if len(frames_spec) < 2:
        raise ValueError('An action needs at least two poses')
    cells, durations = [], []
    # Atlas-level column corrections only; never center each moving silhouette.
    pad = 30 + max(abs(int(n)) for n in offsets)
    for spec in frames_spec:
        c, r = spec['cell']
        duration = spec.get('duration', 120)
        if not (0 <= c < cols and 0 <= r < rows):
            raise ValueError('Cell is outside atlas')
        if not isinstance(duration, int) or duration <= 0 or duration % 10:
            raise ValueError('Duration must be a positive multiple of 10ms')
        sprite = atlas.crop((c * atlas.width // cols, r * atlas.height // rows,
                             (c + 1) * atlas.width // cols, (r + 1) * atlas.height // rows))
        sprite.putalpha(sprite.getchannel('A').point(lambda a: 255 if a >= 144 else 0))
        if not sprite.getbbox():
            raise ValueError('Empty sprite cell')
        layer = Image.new('RGBA', (round(atlas.width / cols) + 2 * pad,
                                   round(atlas.height / rows) + 4))
        layer.alpha_composite(sprite, (pad - int(offsets[c]), 0))
        cells.append(layer)
        durations.append(duration)
    boxes = [cell.getbbox() for cell in cells]
    box = (min(b[0] for b in boxes), min(b[1] for b in boxes),
           max(b[2] for b in boxes), max(b[3] for b in boxes))
    scale = min(108 / (box[3] - box[1]), 124 / (box[2] - box[0]))
    size = (round((box[2] - box[0]) * scale), round((box[3] - box[1]) * scale))
    caption = pack.make_caption(entry['text'], entry.get('ink', '#34324F'), font, 0)
    frames = []
    for cell in cells:
        art = cell.crop(box).resize(size, Image.Resampling.NEAREST)
        frame = Image.new('RGBA', (160, 160))
        frame.alpha_composite(art, ((160 - size[0]) // 2, 122 - size[1]))
        frame = pack.outlined(frame, 1).resize((320, 320), Image.Resampling.NEAREST)
        frame.alpha_composite(caption)
        frames.append(frame)
    palette_sheet = Image.new('RGB', (320 * min(4, len(frames)), 320 * ((len(frames) + 3) // 4)), pack.WHITE)
    for i, frame in enumerate(frames):
        palette_sheet.paste(frame, (i % 4 * 320, i // 4 * 320), frame)
    palette = palette_sheet.quantize(colors=250)
    indexed = []
    for frame in frames:
        matte = Image.new('RGB', frame.size, pack.WHITE)
        matte.paste(frame, (0, 0), frame)
        image = matte.quantize(palette=palette, dither=Image.Dither.NONE)
        image.paste(255, mask=ImageChops.invert(frame.getchannel('A')))
        indexed.append(image)
    target = output / (pack.clean_filename(entry['name']) + '.gif')
    indexed[0].save(target, save_all=True, append_images=indexed[1:], duration=durations,
                    loop=0, disposal=2, transparency=255, optimize=False)
    with Image.open(target) as gif:
        decoded = [f.convert('RGBA') for f in ImageSequence.Iterator(gif)]
        actual_duration = sum(f.info['duration'] for f in ImageSequence.Iterator(gif))
        if gif.size != (320, 320) or gif.info.get('loop') != 0 or actual_duration != sum(durations):
            raise ValueError('Decoded GIF dimensions, loop or timing mismatch')
        if len({f.tobytes() for f in decoded}) < 2:
            raise ValueError('No visible motion')
        for frame in decoded:
            alpha = frame.getchannel('A')
            bounds = alpha.getbbox()
            if set(alpha.getdata()) != {0, 255} or not bounds or min(bounds[:2]) <= 0 or max(bounds[2:]) >= 320:
                raise ValueError('Transparency or safe-margin check failed')
    return {'file': target.name, 'decoded_frames': len(decoded), 'loop_ms': actual_duration,
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'column_offsets': offsets, 'technical_status': 'passed',
            'visual_review': 'pending', 'user_acceptance': 'pending'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--font', required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    names = [pack.clean_filename(e['name']) for e in manifest['entries']]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate output names')
    reports = [render(e, args.manifest.parent, args.output, args.font) for e in manifest['entries']]
    (args.output / 'verification.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2))
    print(json.dumps({'count': len(reports), 'technical_status': 'passed'}))


if __name__ == '__main__':
    main()
