#!/usr/bin/env python3
"""Build grouped transparent GIFs and an optional decoded-GIF MP4 preview."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
import hashlib
import html
import json
from math import cos, exp, pi, sin
from pathlib import Path
import re
from subprocess import Popen, PIPE
from urllib.parse import quote
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageSequence

PIXELS = 160
SIZE = 320
TICKS = 24
DELAY = 80
NEAREST = Image.Resampling.NEAREST
WHITE = '#FFF8EF'

ICONS = {
    'spark': ['....#....','....#....','...###...','..#####..','#########','..#####..','...###...','....#....','....#....'],
    'heart': ['.###.###.','#########','#########','#########','.#######.','..#####..','...###...','....#....'],
    'tear': ['....#....','...###...','...###...','..#####..','.#######.','.#######.','..#####..','...###...'],
    'check': ['.......##','......##.','.....##..','##..##...','.####....','..##.....'],
    'question': ['..####.','.##..##','.....##','....##.','...##..','...##..','.......','...##..'],
    'alert': ['##','##','##','##','##','..','##','##'],
    'sleep': ['######','....##','...##.','..##..','.##...','######'],
    'steam': ['...##....','..####...','.######..','#########','.#######.','..#####..','...#.....','..#......'],
    'note': ['....####','....####','....#...','....#...','....#...','.####...','#####...','.###....'],
    'cross': ['##...##','.##.##.','..###..','...#...','..###..','.##.##.','##...##'],
    'bubble': ['..####..','.##..##.','##....##','##....##','.##..##.','..####..'],
    'dots': ['##.##.##','##.##.##'],
    'bolt': ['....##.','...##..','..##...','.######','....##.','...##..','..##...'],
    'arrow': ['....##.','.....##','#######','#######','.....##','....##.'],
    'petal': ['..##..','.####.','######','.####.','..##..'],
}

MOTIONS = {
    'nod','jump','sway','startle','tremble','ponder','breathe','stomp',
    'rush','peek','pulse','pop','offer','lean','droop','dance',
}

@dataclass(frozen=True)
class Job:
    number: int
    entry: dict
    atlas: str
    grid: tuple
    ink: str
    tint: str
    folder: str
    font: str
    font_index: int
    render_style: str = 'hd'

def pulse(t, at, width):
    return exp(-((t-at)/width)**2)

def motion(kind, t):
    wave = sin(2*pi*t)
    shake = sin(8*pi*t)
    hit = pulse(t,.34,.13)
    if kind == 'nod':
        return 0, 4*hit, 4*hit, 1.5*wave
    if kind == 'jump':
        return 0, -13*hit+4*pulse(t,.14,.08), -3*hit+4*pulse(t,.14,.08), 2*wave
    if kind == 'sway':
        return 3*wave, 0, cos(2*pi*t), 6*wave
    if kind == 'startle':
        return 2*wave, -11*pulse(t,.27,.09)+3*pulse(t,.43,.09), -3*hit, -5*hit+2*wave
    if kind == 'tremble':
        return 3*shake, 1.6*cos(8*pi*t), 2*shake, 2*cos(8*pi*t)
    if kind == 'ponder':
        return wave, 0, wave, 8*pulse(t,.51,.21)
    if kind == 'breathe':
        return 0, 1.8*wave, 3*wave, 2*wave
    if kind == 'stomp':
        return 6*shake*hit, 3*pulse(t,.46,.08), 4*pulse(t,.46,.08), -5*shake*hit
    if kind == 'rush':
        return 10*wave, -6*(.5-.5*cos(4*pi*t)), 1, 5+3*wave
    if kind == 'peek':
        return 6*wave, -2*hit, 0, -4*wave
    if kind == 'pulse':
        return 0, -4*hit, 3*cos(4*pi*t), 3*wave
    if kind == 'pop':
        return 4*hit, -6*hit, -4*hit, 4*wave
    if kind == 'offer':
        return 2*wave, -2*hit, 4*hit, -3*wave
    if kind == 'lean':
        return 4*hit, 2*hit, 1, 8*hit
    if kind == 'droop':
        return -2*wave, 5*hit, 5*hit, -5*hit
    if kind == 'dance':
        return 4*wave, -6*(.5-.5*cos(4*pi*t)), 2*cos(4*pi*t), 6*wave
    raise ValueError(f'Unknown motion {kind!r}')

def outlined(layer, radius):
    border = Image.new('RGBA',layer.size,WHITE)
    border.putalpha(layer.getchannel('A').filter(ImageFilter.MaxFilter(radius*2+1)))
    border.alpha_composite(layer)
    return border

def draw_icon(layer, name, x, y, size, color, ink):
    if size < 1:
        return
    rows=ICONS[name]
    w,h=len(rows[0])*size,len(rows)*size
    mask=Image.new('L',(w+4,h+4))
    pen=ImageDraw.Draw(mask)
    for j,row in enumerate(rows):
        for k,cell in enumerate(row):
            if cell=='#':
                pen.rectangle((2+k*size,2+j*size,1+(k+1)*size,1+(j+1)*size),fill=255)
    badge=Image.new('RGBA',mask.size,ink)
    badge.putalpha(mask.filter(ImageFilter.MaxFilter(3)))
    face=Image.new('RGBA',mask.size,color)
    face.putalpha(mask)
    badge.alpha_composite(face)
    layer.alpha_composite(badge,(round(x-badge.width/2),round(y-badge.height/2)))

def effects(layer, icon, t, tint, ink, seed):
    if icon == 'none':
        return
    polarity = 1 if seed%2 else -1
    wave = sin(2*pi*t)
    hit = pulse(t,.33,.15)
    center = 124 if polarity > 0 else 36
    other = 160-center
    if icon in {'heart','petal','bubble','note','sleep'}:
        for j in range(3):
            phase=(t+j/3)%1
            size=1+int(.12<phase<.86)+int(.44<phase<.68 and j==0)
            draw_icon(layer,icon,center+polarity*(phase*10-j*5),81-44*phase-j*5,size,tint,ink)
        draw_icon(layer,'spark',other,53+3*wave,1,tint,ink)
    elif icon == 'tear':
        for j in range(4):
            phase=(2*t+j*.23)%1
            sign=1 if j%2 else -1
            draw_icon(layer,icon,80+sign*(42+phase*10),76+phase*37+(j//2)*8,
                      1+int(.16<phase<.74),tint,ink)
    else:
        draw_icon(layer,icon,center+2*wave,38-6*hit,2+int(hit>.57),tint,ink)
        draw_icon(layer,'spark' if icon in {'check','spark','question'} else 'dots',
                  other,65+4*wave,1+int(icon=='spark' and hit>.5),tint,ink)
        pen=ImageDraw.Draw(layer)
        pen.line((other-4,82,other+2,79),fill=tint,width=2)

def crop_sprite(job):
    with Image.open(job.atlas) as image:
        atlas=image.convert('RGBA')
    cols,rows=job.grid
    col,row=job.entry['cell']
    w,h=atlas.size
    bounds=job.entry.get('crop',[col*w//cols,row*h//rows,(col+1)*w//cols,(row+1)*h//rows])
    art=atlas.crop(bounds)
    alpha=art.getchannel('A').point(lambda a:255 if a>=144 else 0)
    if alpha.getbbox() is None:
        raise ValueError(f'No transparent sprite in cell {job.entry["cell"]} of {job.atlas}')
    art.putalpha(alpha)
    art=art.crop(alpha.getbbox())
    if job.render_style == 'hd':
        return art
    ratio=min(106/art.height,118/art.width)
    return art.resize((max(1,round(art.width*ratio)),max(1,round(art.height*ratio))),NEAREST)

def make_caption(text, ink, font_path, font_index):
    face=Image.new('RGBA',(SIZE,SIZE))
    d=ImageDraw.Draw(face)
    text=text.translate(str.maketrans({'！':'!','？':'?','～':'~'}))
    size=43 if len(text)<=4 else 38
    font=ImageFont.truetype(font_path,size,index=font_index)
    while font.getlength(text)>275:
        size-=1
        font=ImageFont.truetype(font_path,size,index=font_index)
    d.text((160,278),text,font=font,anchor='mm',fill=ink,stroke_width=1,stroke_fill=ink)
    face.putalpha(face.getchannel('A').point(lambda a:255 if a>=112 else 0))
    return outlined(face,4)

def draw_frame(sprite, label, job, t):
    dx,dy,squash,sway=motion(job.entry['motion'],t)
    layer=Image.new('RGBA',(PIXELS,PIXELS))
    w,h=sprite.size
    art=sprite.resize((w+round(squash),h-round(squash)),NEAREST)
    x=round((PIXELS-art.width)/2+dx)
    y=max(4,round(122-art.height+dy))
    for top in range(0,art.height,3):
        bottom=min(art.height,top+3)
        shear=round((1-top/art.height)**1.7*sway)
        layer.alpha_composite(art.crop((0,top,art.width,bottom)),(x+shear,y+top))
    effects(layer,job.entry['icon'],t,job.tint,job.ink,job.number)
    composite=outlined(layer,2).resize((SIZE,SIZE),NEAREST)
    composite.alpha_composite(label)
    return composite

def make_hd_caption(text, ink, font_path, font_index):
    face=Image.new('RGBA',(512,512))
    pen=ImageDraw.Draw(face)
    size=62 if len(text)<=4 else 56
    font=ImageFont.truetype(font_path,size,index=font_index)
    while font.getlength(text)>440:
        size-=1
        font=ImageFont.truetype(font_path,size,index=font_index)
    pen.text((256,450),text,font=font,anchor='mm',fill=ink,stroke_width=1,stroke_fill=ink)
    return outlined(face,4)


def draw_hd_frame(source, label, job, t):
    # Sample the original crop for every frame, never a reduced pixel sprite.
    size=512
    scale=size/160
    ratio=min(330/source.height,400/source.width)
    base_w,base_h=round(source.width*ratio),round(source.height*ratio)
    dx,dy,squash,sway=motion(job.entry['motion'],t)
    w=max(1,base_w+round(squash*scale))
    h=max(1,base_h-round(squash*scale))
    art=source.resize((w,h),Image.Resampling.LANCZOS)
    pad=45
    padded=Image.new('RGBA',(w+pad*2,h))
    padded.alpha_composite(art,(pad,0))
    shear=sway*scale
    art=padded.transform(padded.size,Image.Transform.AFFINE,
                         (1,shear/h,-shear,0,1,0),Image.Resampling.BICUBIC)
    layer=Image.new('RGBA',(size,size))
    layer.alpha_composite(art,(round((size-w)/2+dx*scale)-pad,
                               round(390-h+dy*scale)))
    accents=Image.new('RGBA',(160,160))
    effects(accents,job.entry['icon'],t,job.tint,job.ink,job.number)
    layer.alpha_composite(accents.resize((size,size),NEAREST))
    layer=outlined(layer,3)
    layer.alpha_composite(label)
    layer.putalpha(layer.getchannel('A').point(lambda a:255 if a>=128 else 0))
    return layer


def save_gif(path, frames):
    size=frames[0].width
    palette_input=Image.new('RGB',(size*4,size*6),WHITE)
    for j,im in enumerate(frames):
        palette_input.paste(im,(size*(j%4),size*(j//4)),im.getchannel('A'))
    palette=palette_input.quantize(colors=250)
    indexed=[]
    for im in frames:
        matte=Image.new('RGB',im.size,WHITE)
        alpha=im.getchannel('A')
        matte.paste(im,(0,0),alpha)
        img=matte.quantize(palette=palette,dither=Image.Dither.NONE)
        img.paste(255,mask=ImageChops.invert(alpha))
        indexed.append(img)
    indexed[0].save(path,save_all=True,append_images=indexed[1:],duration=DELAY,loop=0,
                    disposal=2,transparency=255,optimize=False)

def clean_filename(text):
    return re.sub(r'[\\/:*?"<>|\x00-\x1f]', '_', text)

def verify(path, expected_size=None):
    frames=set()
    duration=0
    with Image.open(path) as image:
        size=image.width
        if size not in {320,512} or image.height!=size or (expected_size is not None and size!=expected_size) or image.info.get('loop')!=0:
            raise ValueError(f'Invalid size or loop flag: {path}')
        for frame in ImageSequence.Iterator(image):
            duration+=frame.info['duration']
            rendered=frame.convert('RGBA')
            alpha=rendered.getchannel('A')
            box=alpha.getbbox()
            if alpha.getextrema()!=(0,255) or box is None or not all(0<k<size for k in box):
                raise ValueError(f'Invalid alpha or clipped content: {path}')
            frames.add(hashlib.sha256(rendered.tobytes()).digest())
    if duration!=TICKS*DELAY or len(frames)<4:
        raise ValueError(f'Missing or inadequate motion: {path}')
    return len(frames)

def build_one(job):
    sprite=crop_sprite(job)
    if job.render_style == 'hd':
        label=make_hd_caption(job.entry['text'],job.ink,job.font,job.font_index)
        frames=[draw_hd_frame(sprite,label,job,k/TICKS) for k in range(TICKS)]
    else:
        label=make_caption(job.entry['text'],job.ink,job.font,job.font_index)
        frames=[draw_frame(sprite,label,job,k/TICKS) for k in range(TICKS)]
    path=Path(job.folder)/f'{job.number:03d}-{clean_filename(job.entry["text"])}.gif'
    save_gif(path,frames)
    poses=hashlib.sha256(sprite.tobytes()).hexdigest()
    return path,poses,verify(path,512 if job.render_style=='hd' else 320)

def gallery(title, groups, folder, render_style='hd'):
    image_rendering='pixelated' if render_style=='pixel' else 'auto'
    text=html.escape(title)
    tabs=[]
    content=[]
    for n,(group,paths) in enumerate(groups):
        name=html.escape(group['name'])
        tabs.append(f'<button type="button" data-section="{n}">{name} · {len(paths)}</button>')
        items=[]
        for path in paths:
            src=quote(path.relative_to(folder).as_posix())
            caption=html.escape(path.stem)
            items.append(f'<a href="{src}"><img loading="lazy" alt="{caption}" data-src="{src}" width="160" height="160"><span>{caption}</span></a>')
        content.append(f'<section id="s{n}" hidden><h2>{name}</h2><div class="grid">{"".join(items)}</div></section>')
    page=f"""<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{text}</title>
<style>
*{{box-sizing:border-box}}body{{margin:auto;max-width:1100px;padding:30px 20px;background:#f3edf8;color:#2e253d;font:16px system-ui,sans-serif}}
h1{{font-size:clamp(24px,5vw,43px);margin:0}}p{{color:#5d4b70}}nav{{display:flex;gap:8px;flex-wrap:wrap;margin:22px 0}}
button{{font:inherit;border:1px solid #cbbcd7;border-radius:10px;padding:9px 12px;background:#fff9f4;color:inherit;cursor:pointer}}button[aria-pressed="true"]{{background:#372946;color:white}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(135px,1fr));gap:12px}}a{{display:grid;justify-items:center;background:#fffaf6;border:1px solid #dccde4;border-radius:12px;padding:8px;text-decoration:none;color:inherit}}img{{width:100%;height:auto;max-width:180px;image-rendering:{image_rendering}}}span{{padding-bottom:4px;font-size:13px}}
</style>
<header><h1>{text}</h1><p>选择分类播放 GIF。点击任意一张可单独打开。</p></header>
<nav>{"".join(tabs)}</nav>{"".join(content)}
<script>
function show(i) {{
  document.querySelectorAll('section').forEach((s,n)=>{{
    s.hidden=n!==i;
    if(n===i) s.querySelectorAll('img[data-src]').forEach(img=>{{img.src=img.dataset.src;delete img.dataset.src}});
  }});
  document.querySelectorAll('button').forEach((b,n)=>b.setAttribute('aria-pressed',n===i));
}}
document.querySelectorAll('button').forEach((b,n)=>b.addEventListener('click',()=>show(n)));
show(0);
</script>
</html>"""
    (folder/'动图浏览.html').write_text(page,encoding='utf-8')

def decoded_frames(path, scale):
    items=[]
    with Image.open(path) as img:
        for frame in ImageSequence.Iterator(img):
            sampling=NEAREST if img.width==320 else Image.Resampling.LANCZOS
            scaled=frame.convert('RGBA').resize((scale,scale),sampling)
            items.extend([scaled]*(frame.info['duration']//DELAY))
    if len(items)!=TICKS:
        raise ValueError(f'Unexpected timing in {path}')
    return items

def preview(title, groups, path, font_path, font_index):
    width,height=1440,1000
    video=Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
                 '-s',f'{width}x{height}','-framerate','25','-i','pipe:0','-c:v','libx264',
                 '-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=PIPE)
    title_font=ImageFont.truetype(font_path,46,index=font_index)
    small=ImageFont.truetype(font_path,23,index=font_index)
    code=ImageFont.truetype(font_path,15,index=font_index)
    try:
        with video.stdin:
            for chapter,(group,files) in enumerate(groups,1):
                for start in range(0,len(files),16):
                    chapter_files=files[start:start+16]
                    base=Image.new('RGB',(width,height),'#F3EDF8')
                    pen=ImageDraw.Draw(base)
                    pen.text((43,25),title,fill='#342B49',font=title_font)
                    pen.text((45,96),f'{chapter:02d} / {len(groups):02d}    {group["name"]}',fill=group['ink'],font=small)
                    pen.line((44,138,1396,138),fill='#C2B0D0',width=2)
                    cols=4 if len(chapter_files)>4 else min(2,len(chapter_files))
                    card_w=(1352-(cols-1)*12)//cols
                    card_h=193 if len(chapter_files)>4 else 382
                    tile_size=186 if len(chapter_files)>4 else 318
                    anchors=[]
                    for i,item in enumerate(chapter_files):
                        x=44+(i%cols)*(card_w+12)
                        y=157+(i//cols)*(card_h+12)
                        pen.rounded_rectangle((x,y,x+card_w,y+card_h),radius=12,fill=group['background'])
                        pen.text((x+14,y+10),item.stem.split('-',1)[0],fill=group['ink'],font=code)
                        anchors.append((x+(card_w-tile_size)//2,y+(card_h-tile_size)//2))
                    decoded=[decoded_frames(p,tile_size) for p in chapter_files]
                    for k in range(TICKS*2):
                        im=base.copy()
                        for timeline,xy in zip(decoded,anchors):
                            tile=timeline[k%TICKS]
                            im.paste(tile,xy,tile.getchannel('A'))
                        raw=im.tobytes()
                        video.stdin.write(raw)
                        video.stdin.write(raw)
    finally:
        status=video.wait()
        if status:
            raise RuntimeError(f'FFmpeg returned {status}')

def clean_preview(groups, path):
    # A header-free grid built from the delivered GIFs, at native resolution.
    files=[p for _,paths in groups for p in paths]
    count=min(16,len(files))
    cols=1 if count==1 else (2 if count<=4 else 4)
    rows=(count+cols-1)//cols
    with Image.open(files[0]) as first:
        tile=first.width
    width,height=cols*tile,rows*tile
    video=Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
                 '-s',f'{width}x{height}','-framerate','25','-i','pipe:0','-c:v','libx264',
                 '-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=PIPE)
    try:
        with video.stdin:
            for start in range(0,len(files),16):
                decoded=[decoded_frames(p,tile) for p in files[start:start+16]]
                for k in range(TICKS*2):
                    im=Image.new('RGB',(width,height),'#EFF2F5')
                    for j,timeline in enumerate(decoded):
                        frame=timeline[k%TICKS]
                        im.paste(frame,((j%cols)*tile,(j//cols)*tile),frame.getchannel('A'))
                    raw=im.tobytes()
                    video.stdin.write(raw)
                    video.stdin.write(raw)
    finally:
        status=video.wait()
        if status:
            raise RuntimeError(f'FFmpeg returned {status}')


def export(args):
    manifest=json.loads(args.manifest.read_text(encoding='utf-8'))
    style=args.render_style or manifest.get('render_style','hd')
    if style not in {'hd','pixel'}:
        raise ValueError('render_style must be hd or pixel')
    count=manifest['count']
    groups=[]
    jobs=[]
    all_text=set()
    seen_cells=set()
    args.output.mkdir(parents=True,exist_ok=True)
    folder=args.output/'GIF合集'
    folder.mkdir()
    for idx,group in enumerate(manifest['groups'],1):
        group_dir=folder/f'{idx:02d}-{clean_filename(group["name"])}'
        group_dir.mkdir()
        first=len(jobs)
        atlas=str((args.manifest.parent/group['atlas']).resolve())
        cols,rows=group['grid']
        for entry in group['entries']:
            txt=entry['text'].strip()
            cell=tuple(entry['cell'])
            assert len(cell)==2 and 0<=cell[0]<cols and 0<=cell[1]<rows
            assert txt and txt not in all_text, f'Duplicate or empty text: {txt}'
            assert (atlas,cell) not in seen_cells, f'Duplicate atlas cell: {atlas} {cell}'
            assert entry['motion'] in MOTIONS and entry['icon'] in {*ICONS,'none'}
            all_text.add(txt)
            seen_cells.add((atlas,cell))
            jobs.append(Job(len(jobs)+1,entry,atlas,(cols,rows),group['ink'],group['tint'],
                            str(group_dir),args.font,args.font_index,style))
        groups.append((group,slice(first,len(jobs))))
    assert len(jobs)==count and jobs
    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        results=list(executor.map(build_one,jobs))
    paths=[item[0] for item in results]
    assert len(set(item[1] for item in results))==count,'Duplicate visual poses'
    visible_groups=[(group,paths[span]) for group,span in groups]
    gallery(manifest['title'],visible_groups,folder,style)
    bundle=args.output/f'{clean_filename(manifest["title"])}-{count}张GIF.zip'
    with ZipFile(bundle,'w',ZIP_DEFLATED) as z:
        for path in [*paths,folder/'动图浏览.html']:
            z.write(path,path.relative_to(folder).as_posix())
    with ZipFile(bundle) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.endswith('.gif')])==count
        for path in paths:
            assert z.read(path.relative_to(folder).as_posix())==path.read_bytes()
    if args.preview:
        layout=args.preview_layout or ('clean' if style=='hd' else 'chapters')
        if layout=='clean':
            clean_preview(visible_groups,args.output/'动态预览.mp4')
        else:
            preview(manifest['title'],visible_groups,args.output/'动态预览.mp4',args.font,args.font_index)
    print(json.dumps({'gif_count':count,'unique_art':count,'unique_frame_min':min(r[2] for r in results),
                      'render_style':style,'size':512 if style=='hd' else 320,
                      'zip':str(bundle),'preview':args.preview},ensure_ascii=False))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('output',type=Path,help='Empty working destination')
    parser.add_argument('--font',required=True,help='Local font file covering all caption glyphs')
    parser.add_argument('--font-index',type=int,default=0)
    parser.add_argument('--jobs',type=int,default=4)
    parser.add_argument('--render-style',choices=['hd','pixel'],help='Default: manifest render_style, otherwise hd (512px); pixel preserves the 320px pixel-art path')
    parser.add_argument('--preview-layout',choices=['clean','chapters'],help='Default: clean for hd; chapters for pixel')
    parser.add_argument('--preview',action='store_true',help='Build an MP4 from actual decoded GIF frames')
    export(parser.parse_args())

if __name__=='__main__':
    main()
