#!/usr/bin/env python3
"""Rebuild paginated previews from saved title frames; requires Pillow."""
import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def main():
    skill = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=skill / 'assets/style-catalog/catalog.json')
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--select', choices=['all', 'selected', 'new', 'handwriting', 'handwriting-scenes'], default='all')
    parser.add_argument('--columns', type=int, default=2)
    parser.add_argument('--page-size', type=int, default=10)
    parser.add_argument('--tile-width', type=int, default=1180)
    parser.add_argument('--font', type=Path, help='Optional font with Chinese glyph coverage.')
    args = parser.parse_args()
    if args.columns < 1 or args.page_size < 1 or args.tile_width < 240:
        parser.error('Use positive columns/page-size and tile-width >= 240.')
    manifest = args.manifest.resolve()
    data = json.loads(manifest.read_text(encoding='utf-8'))
    styles = data['styles']
    if args.select != 'all':
        key = {'selected': 'selected_original_ids', 'new': 'new_case_ids', 'handwriting': 'handwriting_ids', 'handwriting-scenes': 'handwriting_ids'}[args.select]
        styles = [s for s in styles if s['id'] in data[key]]
    if not styles:
        parser.error('The selection has no cases.')
    inputs = {(manifest.parent / s[k]).resolve() for s in data['styles'] for k in ('image', 'lettering_sample') if k in s} | {manifest}
    pages = math.ceil(len(styles) / args.page_size)
    destinations = [args.out_dir / f'{args.select}-{n + 1:02d}.jpg' for n in range(pages)]
    if any(p.resolve() in inputs for p in destinations):
        parser.error('A preview must not overwrite an input.')
    font_path = args.font
    if font_path is None:
        font_path = next((p for p in [
            Path('/System/Library/Fonts/Hiragino Sans GB.ttc'),
            Path('/System/Library/Fonts/STHeiti Medium.ttc'),
            Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
        ] if p.is_file()), None)
    if font_path is not None and not font_path.is_file():
        parser.error('The requested font is missing.')
    label_size = max(16, round(args.tile_width / 39))
    title_size = max(24, round(args.tile_width / 25))
    label_font = ImageFont.truetype(str(font_path), label_size) if font_path else ImageFont.load_default()
    title_font = ImageFont.truetype(str(font_path), title_size) if font_path else label_font
    width = args.tile_width
    height = round(width / (1.5 if args.select == 'handwriting' else 2.38))
    gap = round(width / 36)
    label_h = round(label_size * 1.65)
    top = round(title_size * 2.2)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for page, destination in enumerate(destinations):
        cases = styles[page * args.page_size:(page + 1) * args.page_size]
        columns = min(args.columns, len(cases))
        rows = math.ceil(len(cases) / columns)
        sheet = Image.new('RGB', (gap + columns * (width + gap), top + rows * (height + label_h + gap)), '#f2eee5')
        draw = ImageDraw.Draw(sheet)
        title = {'all': f'{len(data["styles"])} 类电影片名字形', 'selected': f'已选 {len(styles)} 款原版', 'new': f'新增 {len(styles)} 款电影片头', 'handwriting': f'{len(styles)} 款手写字稿', 'handwriting-scenes': f'{len(styles)} 款手写电影片头'}[args.select]
        if not font_path:
            title = f'{args.select.upper()} | CINEMATIC TITLE LETTERING'
        draw.text((gap, gap), f'{title}  {page + 1}/{pages}', fill='#292a27', font=title_font)
        for index, case in enumerate(cases):
            x = gap + index % columns * (width + gap)
            y = top + index // columns * (height + label_h + gap)
            image_key = 'lettering_sample' if args.select == 'handwriting' and 'lettering_sample' in case else 'image'
            with Image.open(manifest.parent / case[image_key]) as source:
                frame = ImageOps.contain(source.convert('RGB'), (width, height), Image.Resampling.LANCZOS)
            sheet.paste(frame, (x + (width - frame.width) // 2, y + (height - frame.height) // 2))
            case_title = case.get('lettering_title', case['title']) if args.select == 'handwriting' else case['title']
            label = f"{case['id']}  {case['name']}  ·  {case_title}" if font_path else case['id']
            draw.text((x, y + height + label_size // 4), label, fill='#292a27', font=label_font)
        sheet.save(destination, quality=92, subsampling=0)
        print(destination.resolve())


if __name__ == '__main__':
    main()
