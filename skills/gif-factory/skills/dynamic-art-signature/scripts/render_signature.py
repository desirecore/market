#!/usr/bin/env python3
"""Composite accepted signature art into two exclusive timed ink gestures."""
import argparse,json,shutil,subprocess,tempfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,find_objects,distance_transform_edt

def load_art(path,w,h,threshold):
    im=Image.open(path).convert('RGBA').resize((w,h),Image.Resampling.LANCZOS)
    arr=np.array(im);transparent=bool(np.any(arr[:,:,3]<250))
    fg=arr[:,:,3]>20 if transparent else np.array(im.convert('L'))>threshold
    labs,count=label(fg)
    return im,fg,labs,transparent

def inspect(args):
    _,_,labs,_=load_art(args.image,args.width,args.height,args.threshold)
    rows=[]
    for i,sl in enumerate(find_objects(labs),1):
        if sl:
            area=int((labs[sl]==i).sum())
            if area>=args.min_area:rows.append({'id':i,'area':area,'bounds_xyxy':[sl[1].start,sl[0].start,sl[1].stop,sl[0].stop]})
    print(json.dumps(rows,ensure_ascii=False,indent=2))

def bezier_segments(paths,sx,sy):
    out=[]
    for curve in paths:
        a,b,c,d=np.array(curve,float)*[sx,sy]
        ps=[(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for t in np.linspace(0,1,150)]
        out.extend((a,b,float(np.linalg.norm(b-a))) for a,b in zip(ps[:-1],ps[1:]))
    return out

def paint_path(segments,budget,w,h,r):
    im=Image.new('L',(w,h));draw=ImageDraw.Draw(im)
    for a,b,ln in segments:
        if budget<=0:break
        e=a+(b-a)*min(1,budget/max(ln,1e-8));draw.line([tuple(a),tuple(e)],fill=255,width=max(1,int(2*r)))
        for px,py in [a,e]:draw.ellipse((px-r,py-r,px+r,py+r),fill=255)
        budget-=ln
    return np.array(im)>0

def ffmpeg(cmd):
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error',*cmd],check=True)

def render(args):
    cfgpath=Path(args.config).resolve();cfg=json.loads(cfgpath.read_text());image=(cfgpath.parent/cfg['image']).resolve()
    for binary in ['ffmpeg','ffprobe']:
        if not shutil.which(binary):raise ValueError('Required executable missing: '+binary)
    w,h=int(cfg.get('width',960)),int(cfg.get('height',640))
    if w%2 or h%2 or min(w,h)<32:raise ValueError('Use positive even video dimensions >=32')
    _,fg,labs,alpha=load_art(image,w,h,cfg.get('foreground_threshold',60))
    ids=cfg.get('upper_components',[])
    if not ids or any(not np.any(labs==i) for i in ids):raise ValueError('Inspect this image and set valid upper_components')
    upper_fg=np.isin(labs,ids)
    if not np.any(fg&~upper_fg):raise ValueError('Upper selection consumes all ink; repair physical stroke separation')
    nearest=distance_transform_edt(labs==0,return_distances=False,return_indices=True)
    upper=np.isin(labs[tuple(nearest)],ids);y,x=np.mgrid[:h,:w]
    def bounds(sel):
        yy,xx=np.where(sel)
        return int(xx.min())-2,int(xx.max())+2
    tx0,tx1=bounds(upper_fg);bx0,bx1=bounds(fg&~upper_fg)
    tm=cfg.get('timing',{});start=float(tm.get('upper_start',.3));ud=float(tm.get('upper_duration',.14));gap=float(tm.get('gap',1.02));body=float(tm.get('body_duration',.18));terminal=float(tm.get('terminal_duration',.72));duration=float(tm.get('duration',4))
    if min(ud,body,terminal,duration)<=0 or min(start,gap)<0:raise ValueError('Invalid timing')
    second=start+ud+gap;tail_start=second+body;end=tail_start+terminal
    if end>duration-.30:raise ValueError('Allow a final hold before the 0.30s ink reset')
    tail=np.zeros((h,w),bool);segments=[];length=0;r=0
    if cfg.get('tail'):
        t=cfg['tail'];cw,ch=t.get('coordinate_size',[w,h]);sx,sy=w/cw,h/ch
        im=Image.new('L',(w,h));draw=ImageDraw.Draw(im);draw.polygon([(px*sx,py*sy) for px,py in t['region_polygon']],fill=255)
        tail=(np.array(im)>0)&~upper;segments=bezier_segments(t['paths'],sx,sy);length=sum(s[2] for s in segments);r=float(t.get('brush_width',60))*min(sx,sy)/2
        if not segments or r<=0:raise ValueError('Invalid tail pen path')
        complete=paint_path(segments,length+1,w,h,r)
        missing=int((tail&fg&~complete).sum())
        if missing:raise ValueError(f'Tail path misses {missing} ink pixels; fix the path/region')
    out=Path(args.out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='signature-masks-') as tmp:
        tmp=Path(tmp)
        for n in range(round(duration*60)):
            now=n/60;a=np.clip((now-start)/ud,0,1)**1.3;b=np.clip((now-second)/body,0,1)**1.3
            if segments:
                q=1-(1-np.clip((now-tail_start)/terminal,0,1))**2
                drawn=paint_path(segments,q*length,w,h,r) if q>0 else np.zeros((h,w),bool)
                lower=(~upper&~tail&(x<=bx0+(bx1-bx0)*b)&(b>0))|(tail&drawn)
            else:
                elapsed=now-second
                if elapsed<0:progress=0
                elif elapsed<body:progress=.78*(elapsed/body)**1.3
                else:progress=.78+.22*(1-(1-np.clip((elapsed-body)/terminal,0,1))**2)
                lower=~upper&(x<=bx0+(bx1-bx0)*progress)&(progress>0)
            mask=np.where((upper&(x<=tx0+(tx1-tx0)*a)&(a>0))|lower,255,0).astype('uint8')
            Image.fromarray(mask).save(tmp/f'{n:03}.png')
        bg=cfg.get('background','1d1e21');key=cfg.get('key_color','202124')
        # Require hex colors to keep the filter specification unambiguous.
        if len(bg)!=6 or len(key)!=6 or any(c not in '0123456789abcdefABCDEF' for c in bg+key):raise ValueError('Use six-digit hex background/key colors')
        keyfilter='' if alpha else f",colorkey=color=0x{key}:similarity={float(cfg.get('key_similarity',.10))}:blend={float(cfg.get('key_blend',.025))}"
        filters=f'[0:v]scale={w}:{h},format=rgba{keyfilter},split[c][a];[a]alphaextract[ka];[1:v]format=gray[m];[ka][m]blend=all_mode=multiply[alpha];[c][alpha]alphamerge,fade=t=out:st={duration-.3}:d=0.3:alpha=1[ink];[2:v][ink]overlay=shortest=1,format=yuv420p[v]'
        ffmpeg(['-loop','1','-framerate','60','-t',str(duration),'-i',str(image),'-framerate','60','-i',str(tmp/'%03d.png'),'-f','lavfi','-i',f'color=c=0x{bg}:s={w}x{h}:r=60:d={duration}','-filter_complex',filters,'-filter_complex_threads','2','-map','[v]','-t',str(duration),'-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(out)+'.mp4'])
    ffmpeg(['-i',str(out)+'.mp4','-filter_complex','[0:v]fps=25,split[a][b];[a]palettegen=max_colors=256:reserve_transparent=0[p];[b][p]paletteuse=dither=none','-loop','0','-y',str(out)+'.gif'])
    ffmpeg(['-ss',str(end+.1),'-i',str(out)+'.mp4','-frames:v','1','-y',str(out)+'.png'])
    print(json.dumps({'mp4':str(out)+'.mp4','gif':str(out)+'.gif','cover':str(out)+'.png','upper_end':start+ud,'second_start':second,'finish':end},ensure_ascii=False))

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('inspect');a.add_argument('--image',required=True);a.add_argument('--width',type=int,default=960);a.add_argument('--height',type=int,default=640);a.add_argument('--threshold',type=float,default=60);a.add_argument('--min-area',type=int,default=90);a.set_defaults(func=inspect)
    a=sub.add_parser('render');a.add_argument('--config',required=True);a.add_argument('--out',required=True);a.set_defaults(func=render)
    args=p.parse_args();args.func(args)
if __name__=='__main__':main()
