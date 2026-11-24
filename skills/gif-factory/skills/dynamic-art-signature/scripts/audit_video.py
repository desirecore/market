#!/usr/bin/env python3
"""Check export metadata and a clean first frame; visual review remains required."""
import argparse,json,subprocess
import numpy as np
p=argparse.ArgumentParser(description=__doc__);p.add_argument('file');p.add_argument('--duration',type=float,default=4);p.add_argument('--fps',type=float,default=60);a=p.parse_args()
r=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,r_frame_rate,nb_frames','-show_entries','format=duration','-of','json',a.file]));s=r['streams'][0];num,den=map(float,s['r_frame_rate'].split('/'));fps=num/den
assert abs(float(r['format']['duration'])-a.duration)<.08,'Wrong duration'
assert abs(fps-a.fps)<.01,'Wrong frame rate'
raw=subprocess.check_output(['ffmpeg','-v','error','-i',a.file,'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
im=np.frombuffer(raw,np.uint8).reshape(s['height'],s['width'],3)
spread=(im.max(axis=(0,1)).astype(int)-im.min(axis=(0,1))).tolist()
assert max(spread)<=4,f'Opening may contain ink/background marks: RGB spread {spread}'
print(json.dumps({'duration':r['format']['duration'],'fps':fps,'size':[s['width'],s['height']],'opening_rgb_spread':spread,'status':'passed','note':'Inspect upper-only hold, body/tail handoff and playback separately.'}))
