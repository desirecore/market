#!/usr/bin/env python3
"""Build small, time-preserving GIF samples from styles/catalog.json."""
import json
from pathlib import Path
from PIL import Image, ImageSequence

ROOT = Path(__file__).resolve().parents[1]

def build():
    report = []
    for style in json.loads((ROOT / 'styles/catalog.json').read_text()):
        for case in style['cases']:
            frames, delays = [], []
            with Image.open(ROOT / case['file']) as source:
                source_loop = source.info.get('loop')
                for frame in ImageSequence.Iterator(source):
                    rgba = frame.convert('RGBA')
                    background = Image.new('RGBA', rgba.size, '#f3f1ea')
                    background.alpha_composite(rgba)
                    image = background.convert('RGB')
                    image.thumbnail((240, 240), Image.Resampling.NEAREST
                                    if style['id'].startswith('pixel') else Image.Resampling.LANCZOS)
                    frames.append(image)
                    delays.append(frame.info.get('duration', 0))
            if not frames or any(delay <= 0 for delay in delays) or source_loop != 0:
                raise ValueError(f"Invalid looping source GIF: {case['file']}")
            sheet = Image.new('RGB', (frames[0].width * 4, frames[0].height))
            for column, index in enumerate((0, len(frames)//4, len(frames)//2, len(frames)*3//4)):
                sheet.paste(frames[index], (column * frames[0].width, 0))
            palette = sheet.quantize(colors=256)
            indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
            dest = ROOT / case['preview']
            dest.parent.mkdir(parents=True, exist_ok=True)
            indexed[0].save(dest, save_all=True, append_images=indexed[1:], duration=delays,
                            loop=0, optimize=False, disposal=1)
            with Image.open(dest) as result:
                decoded = [frame.convert('RGB') for frame in ImageSequence.Iterator(result)]
                result.seek(0)
                actual = sum(frame.info.get('duration', 0) for frame in ImageSequence.Iterator(result))
                if actual != sum(delays) or len({frame.tobytes() for frame in decoded}) < 2:
                    raise RuntimeError(f'Preview lost duration or visible change: {dest}')
                report.append({'style': style['id'], 'source': case['file'], 'preview': case['preview'],
                               'duration_ms': actual, 'frames': result.n_frames, 'loop': 0})
    (ROOT / 'docs/previews/review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f'Built and decoded {len(report)} animated previews.')

if __name__ == '__main__':
    build()
