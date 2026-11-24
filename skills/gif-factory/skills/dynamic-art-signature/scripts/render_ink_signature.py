#!/usr/bin/env python3
"""Adapt signature motion to the actual ink, with optional moving ink fragments.

This renderer reads no reference-video frames or captured animation. Each moving
piece is cut from the supplied static ink, moves/turns/scales, then returns to its
original pixels. Seeded Voronoi ownership preserves complete coverage.
"""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
from PIL import Image
from ink_geometry import stroke_profile, reveal_times, fragment_defaults
from signature_palettes import apply_palette


def smooth(a):
    a=np.clip(a,0,1)
    return a*a*(3-2*a)


@dataclass
class Fragment:
    image: Image.Image
    negative: object
    center: tuple
    birth: float
    land: float
    offset: tuple
    angle: float
    arc: float
    phase: float


class InkAnimation:
    def __init__(self,config_path):
        self.config_path=Path(config_path)
        self.cfg=json.loads(self.config_path.read_text(encoding='utf-8'))
        raw=Image.open(self.config_path.parent/self.cfg['art']).convert('RGBA')
        self.bg=tuple(self.cfg.get('background',[29,30,33]))
        if len(self.bg)!=3 or any(not 0<=v<=255 for v in self.bg):
            raise ValueError('background must contain three RGB values from 0 to 255')
        self.art=Image.alpha_composite(Image.new('RGBA',raw.size,(*self.bg,255)),raw).convert('RGB')
        self.w,self.h=self.art.size
        if min(self.w,self.h)<32 or self.w%2 or self.h%2:
            raise ValueError('Use even video dimensions of at least 32 pixels')
        self.duration=float(self.cfg.get('duration',4))
        self.fps=int(self.cfg.get('fps',60))
        if not np.isfinite(self.duration) or self.duration<=0 or self.fps<=0:
            raise ValueError('duration and fps must be positive')
        self.masks={name:np.zeros((self.h,self.w),bool) for name in ['upper','first','rest','tail']}
        for name,path in self.cfg['masks'].items():
            if name not in self.masks:raise ValueError('Unknown ink layer: '+name)
            mask=np.asarray(Image.open(self.config_path.parent/path).convert('L'))>0
            if mask.shape!=(self.h,self.w):raise ValueError('Each mask must match the art dimensions')
            self.masks[name]=mask
        if np.max(np.sum(list(self.masks.values()),axis=0))>1:
            raise ValueError('Ink layers overlap; repair the current artwork masks')
        self.delta=np.asarray(self.art,dtype=np.float32)-np.asarray(self.bg,dtype=np.float32)
        covered=np.any(list(self.masks.values()),axis=0)
        strength=np.max(np.abs(self.delta),axis=2)
        if 'palette' in self.cfg:
            alpha = raw.getchannel('A')
            if alpha.getextrema()[0] < 255:
                strength = np.asarray(alpha)
        meaningful=strength>float(self.cfg.get('ink_threshold',8))
        missing=meaningful&~covered
        self.unassigned_pixels=int(missing.sum())
        if self.unassigned_pixels>max(8,int(meaningful.sum()*.01)):
            raise ValueError(f'{self.unassigned_pixels} ink pixels are unassigned; fix masks before rendering')
        for name in self.masks:self.masks[name]&=strength>0
        self.has_upper = 'upper' in self.cfg['masks']
        if self.has_upper and not self.masks['upper'].any():
            raise ValueError('The upper mask is empty; omit it for a word-only signature')
        if not (self.masks['first']|self.masks['rest']).any():
            raise ValueError('A name ink layer is required')
        if 'palette' in self.cfg:
            # Resolve the original ink geometry before changing the foreground or backdrop.
            self.bg, self.art = apply_palette(
                self.cfg['palette'], raw, covered & (strength > 0), self.bg)
            self.delta = np.asarray(self.art, dtype=np.float32) - np.asarray(self.bg, dtype=np.float32)
        self.effect=self.cfg.get('effect','ink-fragments' if 'fragments' in self.cfg else 'write')
        if self.effect not in ['write','ink-fragments']:raise ValueError('effect must be write or ink-fragments')
        if self.effect=='write':
            self.masks['first']|=self.masks['rest'];self.masks['rest'][:]=False
        lower=self.masks['first']|self.masks['rest']|self.masks['tail']
        self.profile=stroke_profile(lower)
        if self.has_upper:
            upper_start, upper_end, first_start = .30, .44, 1.46
            body_duration = .16 if self.profile['median_width_px'] <= 5*self.w/960 else .18
        else:
            upper_start, upper_end, first_start = 0., 0., .30
            body_duration = 1.20
        first_end = first_start + body_duration
        self.t={'upper_start':upper_start,'upper_end':upper_end,'first_start':first_start,
                'first_end':first_end,'tail_start':first_end,'tail_end':first_end+.72,
                'fade_start':self.duration-.30,'fade_end':self.duration}
        self.t.update(self.cfg.get('timing',{}))
        self.t={k:float(v) for k,v in self.t.items()}
        if self.has_upper and not 0 <= self.t['upper_start'] < self.t['upper_end'] < self.t['first_start']:
            raise ValueError('Upper gesture timing must leave a hold before the name starts')
        if (not all(np.isfinite(v) for v in self.t.values())
                or not 0<=self.t['first_start']<self.t['first_end']
                or not self.t['first_end']<=self.t['tail_start']<self.t['tail_end']<self.t['fade_start']<self.t['fade_end']<=self.duration):
            raise ValueError('Timing must leave room for the name, tail, final hold and ink reset')
        self.f=fragment_defaults(self.profile,self.w,self.t)
        self.f.update(self.cfg.get('fragments',{}))
        if min(self.f['cell_width'],self.f['cell_height'],self.f['alpha_power'])<=0:
            raise ValueError('Fragment dimensions and alpha_power must be positive')
        self.f['cell_width']=max(1,int(self.f['cell_width']));self.f['cell_height']=max(1,int(self.f['cell_height']))
        self._plan_fragments()
        self._plan_tail()
        self._plan_upper()
        self.first_times,self.first_front,self.first_report=self._plan_gesture('first',self.t['first_start'],self.t['first_end'])
        if max(self.last_land,self.t['tail_end'])>=self.t['fade_start']:
            raise ValueError('Ink must finish before the final hold and reset')

    def _plan_gesture(self,name,start,end,**kwargs):
        mask=self.masks[name]
        if not mask.any():return np.full(mask.shape,np.inf),.003,{'method':'empty layer','coverage':1.}
        if kwargs.get('path') is None and self.cfg.get(name+'_path') is not None:
            kwargs['path']=self.cfg[name+'_path']
        return reveal_times(mask,start,end,pen=self.cfg.get(name+'_pen'),**kwargs)

    def _plan_upper(self):
        self.upper_times,self.upper_front,self.upper_report=self._plan_gesture(
            'upper',self.t['upper_start'],self.t['upper_end'])

    def _plan_fragments(self):
        mask=self.masks['rest'];ys,xs=np.where(mask)
        self.fragments=[];self.last_land=0.;self.fragment_pixels=int(mask.sum())
        self.owner_image=np.full(mask.shape,-1,np.int32)
        if not len(xs):return
        rng=np.random.default_rng(self.cfg.get('seed',731))
        cw,ch=self.f['cell_width'],self.f['cell_height']
        seeds=[]
        for gy in range(int(ys.min()),int(ys.max())+ch,ch):
            for gx in range(int(xs.min()),int(xs.max())+cw,cw):
                seeds.append((gx+cw*(.5+rng.uniform(-.38,.38)),
                              gy+ch*(.5+rng.uniform(-.38,.38))))
        while len(seeds)<3:seeds.append((float(xs.mean())+len(seeds),float(ys.mean())))
        seeds=np.asarray(seeds)
        points=np.column_stack((xs,ys))
        owners=np.empty(len(xs),np.int32)
        neighbors=np.empty((len(xs),3),np.int32)
        weights=np.empty((len(xs),3),np.float32)
        for start in range(0,len(xs),1500):
            d=np.sum((points[start:start+1500,None,:]-seeds[None,:,:])**2,axis=2)
            near=np.argpartition(d,2,axis=1)[:,:3]
            nd=np.take_along_axis(d,near,axis=1)
            order=np.argsort(nd,axis=1)
            near=np.take_along_axis(near,order,axis=1);nd=np.take_along_axis(nd,order,axis=1)
            softness=self.f.get('edge_softness',1.15)
            w=np.exp(-(nd-nd[:,0:1])/(2*softness*cw));w/=w.sum(axis=1,keepdims=True)
            owners[start:start+len(d)]=near[:,0]
            neighbors[start:start+len(d)]=near
            weights[start:start+len(d)]=w
        owner_image=np.full((self.h,self.w),-1,np.int32);owner_image[ys,xs]=owners
        self.owner_image=owner_image
        # Split premultiplied color contributions with a soft partition of
        # unity. Integer residuals go to the strongest owner, so the final
        # identity transforms reconstruct every original ink pixel exactly.
        colors=self.delta[ys,xs].astype(np.int16)
        contributions=np.floor(np.abs(colors[:,None,:])*weights[:,:,None]).astype(np.int16)
        contributions[:,0,:]+=np.abs(colors)-contributions.sum(axis=1)
        contributions*=np.sign(colors[:,None,:]).astype(np.int16)
        fragments=[]
        width=max(1,float(np.ptp(xs)))
        for owner in np.unique(neighbors):
            selected,slot=np.where(neighbors==owner)
            values=contributions[selected,slot]
            visible=np.any(values!=0,axis=1)
            selected,values=selected[visible],values[visible]
            py,px=ys[selected],xs[selected]
            if not len(px):continue
            left,right=max(0,int(px.min())-2),min(self.w,int(px.max())+3)
            top,bottom=max(0,int(py.min())-2),min(self.h,int(py.max())+3)
            piece=np.zeros((bottom-top,right-left,3),np.uint8)
            piece[py-top,px-left]=np.maximum(values,0).astype(np.uint8)
            image=Image.fromarray(piece)
            negative=None
            if np.any(values<0):
                dark=np.zeros_like(piece)
                dark[py-top,px-left]=np.maximum(-values,0).astype(np.uint8)
                negative=Image.fromarray(dark)
            xnorm=float((px.mean()-xs.min())/width)
            birth=self.f['birth_base']+self.f['birth_spread']*xnorm+rng.uniform(-.055,.045)
            land=self.f['land_base']+self.f['land_spread']*xnorm+rng.uniform(-self.f['time_jitter'],self.f['time_jitter'])
            drift=self.f['drift']
            if land<=birth:raise ValueError('Each fragment must land after it starts')
            fragments.append(Fragment(image,negative,((left+right)/2,(top+bottom)/2),float(birth),float(land),
                                      (float(rng.uniform(-.70,1.1)*drift),float(rng.uniform(-.8,.8)*drift)),
                                      float(rng.uniform(-self.f['rotation'],self.f['rotation'])),
                                      float(rng.uniform(-.35,.35)*drift),float(rng.uniform(0,np.pi*2))))
        self.fragments=fragments
        self.last_land=max((f.land for f in fragments),default=0.)
        assert np.all(owner_image[mask]>=0),'Some ink has no fragment'
        self.fragment_pixels=int(mask.sum())
        assert np.array_equal(contributions.sum(axis=1),colors),'Fragment contributions changed source ink'

    def _plan_tail(self):
        self.tail_times,self.tail_front,self.tail_report=self._plan_gesture(
            'tail',self.t['tail_start'],self.t['tail_end'],
            join_from=self.masks['first']|self.masks['rest'],
            path=self.cfg.get('tail_path'),slowing=True)
        self.tail_error=self.tail_report.get('path_error_px',0.)
        if self.tail_error>max(12*self.w/960,self.profile['p90_width_px']*3):
            raise ValueError('Tail path is too far from its ink; trace this artwork again')

    def frame_at(self,now):
        canvas=np.zeros((self.h,self.w,3),np.float32)
        up=smooth((now-self.upper_times)/self.upper_front)
        first=smooth((now-self.first_times)/self.first_front)
        canvas+=self.delta*up[:,:,None]
        canvas+=self.delta*first[:,:,None]
        for fragment in self.fragments:
            p=float(np.clip((now-fragment.birth)/(fragment.land-fragment.birth),0,1))
            if p<=0:continue
            if p>=1:
                image=fragment.image
                negative=fragment.negative
                x=int(round(fragment.center[0]-image.width/2));y=int(round(fragment.center[1]-image.height/2))
                opacity=1.
            else:
                e=float(smooth(p))
                opacity=p**self.f['alpha_power']
                scale=.52+.48*e
                size=(max(2,round(fragment.image.width*scale)),max(2,round(fragment.image.height*scale)))
                image=fragment.image.resize(size,Image.Resampling.BICUBIC)
                angle=fragment.angle*(1-e)+9*np.sin(np.pi*p)*np.cos(fragment.phase)
                image=image.rotate(angle,Image.Resampling.BICUBIC,expand=True)
                negative=(fragment.negative.resize(size,Image.Resampling.BICUBIC).rotate(
                    angle,Image.Resampling.BICUBIC,expand=True) if fragment.negative else None)
                dx=fragment.offset[0]*(1-e)+fragment.arc*np.sin(np.pi*p)
                dy=fragment.offset[1]*(1-e)+fragment.arc*.6*np.sin(np.pi*p+fragment.phase)*np.sin(np.pi*p)
                x=int(round(fragment.center[0]+dx-image.width/2));y=int(round(fragment.center[1]+dy-image.height/2))
            left,right=max(0,x),min(self.w,x+image.width)
            top,bottom=max(0,y),min(self.h,y+image.height)
            if left<right and top<bottom:
                patch=np.asarray(image,dtype=np.float32)[top-y:bottom-y,left-x:right-x]
                canvas[top:bottom,left:right]+=patch*opacity
                if negative is not None:
                    patch=np.asarray(negative,dtype=np.float32)[top-y:bottom-y,left-x:right-x]
                    canvas[top:bottom,left:right]-=patch*opacity
        tail_alpha=smooth((now-self.tail_times)/self.tail_front)
        canvas+=self.delta*tail_alpha[:,:,None]
        fade=float(np.clip((self.t['fade_end']-now)/(self.t['fade_end']-self.t['fade_start']),0,1))
        rgb=np.clip(np.asarray(self.bg)+canvas*fade,0,255).astype(np.uint8)
        return Image.fromarray(rgb)

    def render(self,out):
        if not shutil.which('ffmpeg'):raise ValueError('Install FFmpeg for MP4 and GIF export')
        out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
        video=out.with_suffix('.mp4')
        command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
                 '-s',f'{self.w}x{self.h}','-r',str(self.fps),'-i','pipe:0','-an',
                 '-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p',
                 '-movflags','+faststart',str(video)]
        with subprocess.Popen(command,stdin=subprocess.PIPE) as process:
            with process.stdin:
                for n in range(round(self.duration*self.fps)):
                    process.stdin.write(self.frame_at(n/self.fps).tobytes())
            if process.wait():raise RuntimeError('Video encoding failed')
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(video),
                        '-filter_complex','[0:v]fps=25,split[a][b];[a]palettegen=max_colors=256:reserve_transparent=0[p];[b][p]paletteuse=dither=none',
                        '-loop','0',str(out.with_suffix('.gif'))],check=True)
        self.frame_at((max(self.last_land,self.t['tail_end'])+self.t['fade_start'])/2).save(out.with_suffix('.png'))
        report=self.report()
        out.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False))

    def report(self):
        report={'size':[self.w,self.h],'duration':self.duration,'fps':self.fps,'gif_fps':25,
                'input_is_static_art':True,'reference_video_used_by_renderer':False,
                'fragments':len(self.fragments),'fragment_pixels':self.fragment_pixels,
                'coverage':float(np.mean(self.owner_image[self.masks['rest']]>=0)) if self.fragment_pixels else 1.,
                'last_fragment_lands':round(self.last_land,4),'tail_path_error_px':round(self.tail_error,3),
                'timing':self.t,'fragment_parameters':self.f}
        report.update({'effect':self.effect,'ink_profile':self.profile,'unassigned_ink_pixels':self.unassigned_pixels,
                       'upper_pen':self.upper_report,'first_pen':self.first_report,'tail_pen':self.tail_report,
                       'exact_calligraphic_order':False})
        if 'palette' in self.cfg:
            report['palette'] = self.cfg['palette']
        return report

    def preview_plan(self,out):
        from PIL import ImageDraw
        out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
        first_start = self.t['first_start']
        first_duration = self.t['first_end'] - first_start
        if self.has_upper:
            upper_start = self.t['upper_start']
            upper_duration = self.t['upper_end'] - upper_start
            times = [upper_start + upper_duration*q for q in (.25, .5, .85)]
            times.append(first_start + first_duration/2)
        else:
            times = [first_start + first_duration*q for q in (.15, .4, .65, .9)]
        times.extend([(self.t['tail_start']+self.t['tail_end'])/2,
                      (max(self.last_land,self.t['tail_end'])+self.t['fade_start'])/2])
        height=round(480*self.h/self.w)
        sheet=Image.new('RGB',(1440,2*(height+24)),self.bg)
        draw=ImageDraw.Draw(sheet)
        label_color = (32, 32, 32) if 'palette' in self.cfg and sum(self.bg) > 450 else (220, 220, 220)
        for i,t in enumerate(times):
            x=(i%3)*480;y=(i//3)*(height+24)
            sheet.paste(self.frame_at(t).resize((480,height),Image.Resampling.LANCZOS),(x,y))
            draw.text((x+10,y+height+4),f'{t:.3f}s',label_color)
        sheet.save(out.with_suffix('.plan.png'))
        out.with_suffix('.plan.json').write_text(json.dumps(self.report(),ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--plan-only',action='store_true',help='Save six actual motion frames and resolved geometry, without encoding')
    args=parser.parse_args();animation=InkAnimation(args.config)
    if args.plan_only:animation.preview_plan(args.out)
    else:animation.render(args.out)
