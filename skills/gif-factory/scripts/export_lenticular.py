#!/usr/bin/env python3
"""Export two already aligned poster states; never crop or invent missing art."""
import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageSequence, ImageStat


def load_state(path, size):
    with Image.open(path) as src:
        if src.width * size[1] != src.height * size[0]:
            raise ValueError(f'{path}: aspect ratio differs from {size}; recompose first')
        rgba = src.convert('RGBA')
    base = Image.new('RGBA', rgba.size, 'black')
    base.alpha_composite(rgba)
    result = base.convert('RGB').resize(size, Image.Resampling.LANCZOS)
    result.info.clear()
    return result


def export(a_path, b_path, output, width=480, height=720, seconds=6, fps=20,
           footer_height=0, title='', subtitle='', font=None, subtitle_font=None):
    if min(width, height) < 1 or fps not in (10, 20, 25, 50):
        raise ValueError('positive dimensions and fps of 10, 20, 25 or 50 required')
    count = round(seconds * fps)
    if not 0 < seconds <= 30 or count < 2 or abs(count - seconds * fps) > 1e-6:
        raise ValueError('duration must produce a whole number of frames (up to 30s)')
    if not 0 <= footer_height < height:
        raise ValueError('footer-height must be inside the canvas')
    if (title or subtitle) and (not font or not footer_height):
        raise ValueError('titles require --font and --footer-height')
    output = Path(output)
    if output.suffix.lower() != '.gif':
        raise ValueError('output must end in .gif')
    a, b = load_state(a_path, (width, height)), load_state(b_path, (width, height))
    if not ImageChops.difference(a, b).getbbox():
        raise ValueError('states are identical; there is no image change')
    footer = None
    if footer_height:
        footer = Image.new('RGB', (width, footer_height), 'black')
        draw = ImageDraw.Draw(footer)
        for text, y, pixels, path, color in [
            (title, 4, min(44, footer_height * 3 // 5), font, '#eeeeeb'),
            (subtitle, footer_height - 15, 11, subtitle_font or font, '#888888'),
        ]:
            if not text:
                continue
            face = ImageFont.truetype(str(path), max(1, pixels))
            while draw.textbbox((0, 0), text, font=face)[2] > width - 16 and face.size > 1:
                face = ImageFont.truetype(str(path), face.size - 1)
            box = draw.textbbox((0, 0), text, font=face)
            draw.text(((width - box[2]) / 2, y), text, font=face, fill=color)
    frames = []
    for i in range(count):
        progress = max(0, min(1, (-math.cos(2 * math.pi * i / count) + .32) / .64))
        row = []
        for x in range(width):
            k = max(0, min(1, (progress + .065 * (x / width - .5) - (x % 3) / 3) / .14 + .5))
            row.append(round(255 * (0 if progress == 0 else 1 if progress == 1 else k)))
        mask = Image.frombytes('L', (width, height), bytes(row) * height)
        frame = Image.composite(b, a, mask)
        if footer:
            frame.paste(footer, (0, height - footer_height))
        frames.append(frame)
    sheet = Image.new('RGB', (width * 3, height))
    for j, i in enumerate((0, count // 4, count // 2)):
        sheet.paste(frames[i], (width * j, 0))
    palette = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    colors = palette.getpalette()[:765] + [0, 0, 0]
    palette.putpalette(colors)
    # Index 255 is reserved. Map an accidental opaque black match to real black,
    # not arbitrary palette index 0 (which can be white or skin colored).
    replacement = min(range(255), key=lambda j: sum(v * v for v in colors[j * 3:j * 3 + 3]))
    remap = bytes([*range(255), replacement])
    encoded = []
    fixed = None
    for frame in frames:
        q = frame.quantize(palette=palette, dither=Image.Dither.NONE)
        q = Image.frombytes('P', (width, height), q.tobytes().translate(remap))
        q.putpalette(colors)
        q.info.clear()
        if footer:
            box = (0, height - footer_height, width, height)
            if fixed is None:
                fixed = q.crop(box)
            q.paste(fixed, box)
        encoded.append(q)
    output.parent.mkdir(parents=True, exist_ok=True)
    encoded[0].save(output, save_all=True, append_images=encoded[1:],
                    duration=1000 // fps, loop=0, disposal=1, optimize=False)
    with Image.open(output) as gif:
        decoded = [f.convert('RGB') for f in ImageSequence.Iterator(gif)]
        gif.seek(0)
        delays = [f.info.get('duration', 0) for f in ImageSequence.Iterator(gif)]
        report = {'file': output.name, 'size': list(gif.size), 'frames': gif.n_frames,
                  'duration_ms': sum(delays), 'sampling_fps': fps, 'loop': gif.info.get('loop')}
    if any(ms <= 0 for ms in delays) or report['duration_ms'] != count * (1000 // fps):
        raise RuntimeError('decoded GIF timing differs from requested timeline')
    if len({f.tobytes() for f in decoded}) < 2:
        raise RuntimeError('palette eliminated the visible image change; revise states')
    seam = ImageStat.Stat(ImageChops.difference(decoded[0], decoded[-1])).mean
    report['seam_mean'] = sum(seam) / len(seam)
    report['fixed_footer'] = not footer or all(
        not ImageChops.difference(decoded[0].crop(box), f.crop(box)).getbbox() for f in decoded)
    output.with_suffix('.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('state_a', 'state_b', 'output'):
        parser.add_argument(name, type=Path)
    parser.add_argument('--width', type=int, default=480)
    parser.add_argument('--height', type=int, default=720)
    parser.add_argument('--seconds', type=float, default=6)
    parser.add_argument('--fps', type=int, default=20)
    parser.add_argument('--footer-height', type=int, default=0)
    parser.add_argument('--title', default='')
    parser.add_argument('--subtitle', default='')
    parser.add_argument('--font', type=Path)
    parser.add_argument('--subtitle-font', type=Path)
    args = vars(parser.parse_args())
    try:
        print(json.dumps(export(args.pop('state_a'), args.pop('state_b'), args.pop('output'), **args), ensure_ascii=False))
    except (ValueError, OSError, RuntimeError) as exc:
        parser.error(str(exc))
