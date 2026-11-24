#!/usr/bin/env python3
"""Assemble saved film-title frames into a portable contact sheet. Requires Pillow."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def main():
    skill = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=skill / 'assets/film-title-examples/prompts.json')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--columns', type=int, default=2)
    parser.add_argument('--tile-width', type=int, default=1000)
    args = parser.parse_args()
    manifest = args.manifest.resolve()
    cases = json.loads(manifest.read_text(encoding='utf-8'))['cases']
    if not cases or not 1 <= args.columns <= len(cases) or args.tile_width < 100:
        parser.error('Use a nonempty manifest, 1..case-count columns and tile-width >= 100.')
    paths = [manifest.parent / case['output'] for case in cases]
    if args.out.resolve() in [p.resolve() for p in paths] or args.out.resolve() == manifest:
        parser.error('The overview must not overwrite an input.')
    width, gap, label_h = args.tile_width, 16, 30
    height = round(width / 2.38)
    rows = (len(cases) + args.columns - 1) // args.columns
    overview = Image.new('RGB', (gap + args.columns * (width + gap), gap + rows * (height + label_h + gap)), '#eeeae1')
    draw = ImageDraw.Draw(overview)
    font = ImageFont.load_default()
    for i, (case, path) in enumerate(zip(cases, paths)):
        with Image.open(path) as source:
            image = ImageOps.contain(source.convert('RGB'), (width, height), Image.Resampling.LANCZOS)
        x, y = gap + i % args.columns * (width + gap), gap + i // args.columns * (height + label_h + gap)
        overview.paste(image, (x + (width-image.width)//2, y + (height-image.height)//2))
        draw.text((x, y + height + 8), case['id'] + '  ' + case['english'], fill='#30332d', font=font)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    overview.save(args.out)
    print(args.out.resolve())


if __name__ == '__main__':
    main()
