#!/usr/bin/env python3
"""Compose nine actual video files, with labels drawn in Pillow for portability."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse,json,subprocess,shutil

def find_font(value=None):
 candidates=[value] if value else [
  '/System/Library/Fonts/Supplemental/Songti.ttc',
  '/System/Library/Fonts/PingFang.ttc',
  '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
  'C:/Windows/Fonts/msyh.ttc']
 for p in candidates:
  if p and Path(p).exists():return str(p)
 raise RuntimeError('Pass --font with a font that supports Chinese labels')

def assemble(videos,labels,out,font=None):
 out=Path(out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 if len(videos)!=9 or len(labels)!=9:raise ValueError('Use exactly nine finished signature videos and labels')
 for binary in ['ffmpeg','ffprobe']:
  if not shutil.which(binary):raise ValueError('Required executable missing: '+binary)
 for video in videos:
  if not Path(video).is_file():raise ValueError('Video not found: '+str(video))
  data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(video)]))
  if abs(float(data['format']['duration'])-4)>.10:raise ValueError('Each grid input must be a four-second finished video: '+str(video))
 overlay=Image.new('RGBA',(1440,1440));d=ImageDraw.Draw(overlay);f=ImageFont.truetype(find_font(font),19)
 for i,title in enumerate(labels):
  x=i%3*480;y=i//3*480
  d.rectangle((x+1,y+1,x+478,y+478),outline=(53,54,59,255),width=1)
  d.text((x+24,y+432),f'{i+1:02d}  {title}',font=f,fill=(167,170,179,255))
 overlay_path=out.parent/'九宫格标签.png';overlay.save(overlay_path)
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y']
 for p in videos:cmd+=['-i',str(p)]
 cmd+=['-loop','1','-framerate','30','-i',str(overlay_path)]
 filters=[f'[{i}:v]fps=30,scale=480:320:flags=lanczos,pad=480:480:0:64:color=0x1d1e21[c{i}]' for i in range(9)]
 layout='|'.join(f'{i%3*480}_{i//3*480}' for i in range(9))
 filters.append(''.join(f'[c{i}]' for i in range(9))+f'xstack=inputs=9:layout={layout}[grid]')
 filters.append('[grid][9:v]overlay=0:0:shortest=1[out]')
 subprocess.run(cmd+['-filter_complex',';'.join(filters),'-filter_complex_threads','2','-map','[out]',
                    '-t','4','-r','30','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','17',
                    '-pix_fmt','yuv420p','-movflags','+faststart',str(out.with_suffix('.mp4'))],check=True)
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(out.with_suffix('.mp4')),
                 '-filter_complex','[0:v]fps=25,scale=1080:1080:flags=lanczos,split[a][b];[a]palettegen=max_colors=256:reserve_transparent=0[p];[b][p]paletteuse=dither=none',
                 '-loop','0',str(out.with_suffix('.gif'))],check=True)
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','2.9','-i',str(out.with_suffix('.mp4')),
                 '-frames:v','1',str(out.with_suffix('.png'))],check=True)
 print(str(out),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--videos',nargs=9,required=True)
 p.add_argument('--labels',nargs=9,required=True)
 p.add_argument('--out',type=Path,required=True)
 p.add_argument('--font')
 a=p.parse_args()
 assemble(a.videos,a.labels,a.out,a.font)
