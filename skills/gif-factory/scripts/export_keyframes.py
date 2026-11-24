#!/usr/bin/env python3
"""Compose articulated 512px GIFs from aligned, generated key poses."""
import argparse
import hashlib
import json
from math import ceil, sqrt
from pathlib import Path
from subprocess import Popen, PIPE
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageSequence

from export_pack import clean_filename, gallery

SIZE = 512
TICK = 20
WHITE = '#FFF8EF'


def make_frames(atlas, grid, entry, font_path, font_index):
    cols, rows = grid
    if cols < 1 or rows < 1:
        raise ValueError('Grid dimensions must be positive')
    w, h = atlas.size
    cells, boxes, durations = [], [], []
    for frame in entry['frames']:
        c, r = frame['cell']
        if not (0 <= c < cols and 0 <= r < rows):
            raise ValueError(f'Cell outside atlas: {frame["cell"]}')
        ms = frame.get('duration', 120)
        if not isinstance(ms, int) or ms < TICK or ms % TICK:
            raise ValueError('Frame duration must be a positive multiple of 20ms')
        bounds = frame.get('crop', [c*w//cols, r*h//rows, (c+1)*w//cols, (r+1)*h//rows])
        if len(bounds) != 4 or not (0 <= bounds[0] < bounds[2] <= w and 0 <= bounds[1] < bounds[3] <= h):
            raise ValueError(f'Invalid crop: {bounds}')
        cell = atlas.crop(bounds)
        target = (w//cols, h//rows)
        if any(abs(a-b) > 1 for a, b in zip(cell.size, target)):
            raise ValueError('Frame crops must share one coordinate frame and cell size')
        cell = cell.resize(target, Image.Resampling.LANCZOS)
        alpha = cell.getchannel('A').point(lambda v: 255 if v >= 144 else 0)
        box = alpha.getbbox()
        if box is None or alpha.getextrema() != (0, 255):
            raise ValueError('Every pose needs a real transparent gutter; inspect the atlas')
        cell.putalpha(alpha)
        cells.append(cell)
        boxes.append(box)
        durations.append(ms)
    if len(cells) < 2:
        raise ValueError('An action requires at least two key poses')
    # A shared crop/scale preserves head and torso anchors as the hands move.
    union = (min(b[0] for b in boxes), min(b[1] for b in boxes),
             max(b[2] for b in boxes), max(b[3] for b in boxes))
    ratio = min(430/(union[2]-union[0]), 360/(union[3]-union[1]))
    tw, th = round((union[2]-union[0])*ratio), round((union[3]-union[1])*ratio)
    label = Image.new('RGBA', (SIZE, SIZE))
    pen = ImageDraw.Draw(label)
    text = entry['text']
    size = 62 if len(text) <= 4 else 56
    font = ImageFont.truetype(font_path, size, index=font_index)
    while font.getlength(text) > 440:
        size -= 1
        font = ImageFont.truetype(font_path, size, index=font_index)
    pen.text((256,450), text, font=font, anchor='mm', fill=entry.get('ink','#303443'),
             stroke_width=4, stroke_fill=WHITE)
    frames = []
    for cell in cells:
        art = cell.crop(union).resize((tw,th), Image.Resampling.LANCZOS)
        layer = Image.new('RGBA', (SIZE,SIZE))
        layer.alpha_composite(art, ((SIZE-tw)//2,398-th))
        border = Image.new('RGBA', layer.size, WHITE)
        border.putalpha(layer.getchannel('A').filter(ImageFilter.MaxFilter(5)))
        border.alpha_composite(layer)
        border.alpha_composite(label)
        border.putalpha(border.getchannel('A').point(lambda v: 255 if v >= 128 else 0))
        frames.append(border)
    return frames, durations


def save_and_verify(path, frames, durations):
    cols = min(4, ceil(sqrt(len(frames))))
    sheet = Image.new('RGB', (SIZE*cols,SIZE*ceil(len(frames)/cols)), WHITE)
    for i, frame in enumerate(frames):
        sheet.paste(frame, (i%cols*SIZE,i//cols*SIZE), frame)
    palette = sheet.quantize(colors=250)
    indexed = []
    for frame in frames:
        matte = Image.new('RGB', frame.size, WHITE)
        matte.paste(frame, (0,0), frame)
        q = matte.quantize(palette=palette, dither=Image.Dither.NONE)
        q.paste(255, mask=ImageChops.invert(frame.getchannel('A')))
        indexed.append(q)
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=durations,
                    loop=0, disposal=2, transparency=255, optimize=False)
    unique, elapsed = set(), 0
    with Image.open(path) as gif:
        if gif.size != (SIZE,SIZE) or gif.info.get('loop') != 0:
            raise ValueError(f'Invalid size/loop: {path}')
        for frame in ImageSequence.Iterator(gif):
            rgba = frame.convert('RGBA')
            alpha = rgba.getchannel('A')
            box = alpha.getbbox()
            if alpha.getextrema() != (0,255) or box is None or not all(0<v<SIZE for v in box):
                raise ValueError(f'Clipped or invalid transparency: {path}')
            unique.add(hashlib.sha256(rgba.tobytes()).digest())
            elapsed += frame.info['duration']
    if elapsed != sum(durations) or len(unique) < 2:
        raise ValueError(f'Missing motion/timing: {path}')
    return len(unique)


def preview(files, path):
    count = min(16,len(files))
    cols = 1 if count == 1 else (2 if count <= 4 else (3 if count <= 9 else 4))
    rows = ceil(count/cols)
    width, height = cols*SIZE, rows*SIZE
    video = Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
                   '-s',f'{width}x{height}','-framerate','50','-i','pipe:0',
                   '-c:v','libx264','-crf','16','-pix_fmt','yuv420p',
                   '-movflags','+faststart',str(path)], stdin=PIPE)
    try:
        with video.stdin:
            for start in range(0,len(files),16):
                timelines = []
                for p in files[start:start+16]:
                    timeline = []
                    with Image.open(p) as gif:
                        for frame in ImageSequence.Iterator(gif):
                            timeline.extend([frame.convert('RGBA')]*(frame.info['duration']//TICK))
                    timelines.append(timeline)
                for k in range(max(map(len,timelines))*3):
                    im = Image.new('RGB',(width,height),'#EFF2F5')
                    for j,timeline in enumerate(timelines):
                        frame = timeline[k%len(timeline)]
                        im.paste(frame,(j%cols*SIZE,j//cols*SIZE),frame)
                    video.stdin.write(im.tobytes())
    finally:
        status = video.wait()
        if status:
            raise RuntimeError(f'FFmpeg returned {status}')


def export(args):
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    folder = args.output/'GIF合集'
    folder.mkdir(parents=True)
    groups, paths, texts, unique_counts = [], [], set(), []
    for group_index, group in enumerate(manifest['groups'],1):
        dest = folder/f'{group_index:02d}-{clean_filename(group["name"])}'
        dest.mkdir()
        with Image.open(args.manifest.parent/group['atlas']) as source:
            atlas = source.convert('RGBA')
        group_paths = []
        for entry in group['entries']:
            text = entry['text'].strip()
            if not text or text in texts:
                raise ValueError(f'Empty or repeated caption: {text}')
            texts.add(text)
            frames, durations = make_frames(atlas,group['grid'],entry,args.font,args.font_index)
            path = dest/f'{len(paths)+1:03d}-{clean_filename(entry.get("name",text))}.gif'
            unique_counts.append(save_and_verify(path,frames,durations))
            group_paths.append(path)
            paths.append(path)
        groups.append((group,group_paths))
    if len(paths) != manifest['count'] or not paths:
        raise ValueError('GIF count does not match manifest')
    if len({hashlib.sha256(p.read_bytes()).digest() for p in paths}) != len(paths):
        raise ValueError('Duplicate animations')
    gallery(manifest['title'],groups,folder,'hd')
    bundle = args.output/f'{clean_filename(manifest["title"])}-{len(paths)}张GIF.zip'
    with ZipFile(bundle,'w',ZIP_DEFLATED) as z:
        for p in [*paths,folder/'动图浏览.html']:
            z.write(p,p.relative_to(folder).as_posix())
        if manifest.get('credits'):
            z.writestr('来源与制作说明.json',json.dumps(manifest['credits'],ensure_ascii=False,indent=2))
    with ZipFile(bundle) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.endswith('.gif')]) == len(paths)
        for p in paths:
            assert z.read(p.relative_to(folder).as_posix()) == p.read_bytes()
    if args.preview:
        preview(paths,args.output/'动态预览.mp4')
    print(json.dumps({'gif_count':len(paths),'size':SIZE,'unique_frame_min':min(unique_counts),
                      'zip':str(bundle),'preview':args.preview},ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('output',type=Path,help='Empty destination')
    parser.add_argument('--font',required=True)
    parser.add_argument('--font-index',type=int,default=0)
    parser.add_argument('--preview',action='store_true')
    export(parser.parse_args())


if __name__ == '__main__':
    main()
