#!/usr/bin/env python3
"""Probe a video and optionally extract start/middle/end frames for review."""
import argparse
import json
import subprocess
from fractions import Fraction
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--fps', type=float)
    parser.add_argument('--duration', type=float)
    parser.add_argument('--frames-dir', type=Path)
    args = parser.parse_args()
    if not args.video.is_file():
        parser.error('video file does not exist')
    for key in ('fps', 'duration'):
        value = getattr(args, key)
        if value is not None and value <= 0:
            parser.error(f'--{key} must be positive')
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
               '-count_frames', '-show_entries',
               'stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames,duration:format=duration',
               '-of', 'json', str(args.video.resolve())]
    data = json.loads(subprocess.check_output(command))
    if not data.get('streams'):
        raise SystemExit('No video stream found')
    stream = data['streams'][0]
    fps = float(Fraction(stream['avg_frame_rate']))
    nominal = float(Fraction(stream['r_frame_rate']))
    if fps <= 0:
        raise SystemExit('Cannot determine positive video frame rate')
    duration = float(stream.get('duration') or data['format']['duration'])
    count = int(stream['nb_read_frames'])
    errors = []
    if args.fps is not None and (abs(fps - args.fps) > .001 or abs(nominal - args.fps) > .001):
        errors.append('Actual or nominal fps differs from requested fps')
    if args.duration is not None and abs(duration - args.duration) > max(.002, .51 / fps):
        errors.append('Duration differs by more than half a frame')
    if args.fps is not None and args.duration is not None and count != round(args.fps * args.duration):
        errors.append('Decoded frame count differs from requested fps * duration')
    frames = []
    if args.frames_dir:
        args.frames_dir.mkdir(parents=True, exist_ok=True)
        for label, index in [('start', 0), ('middle', count // 2), ('end', count - 1)]:
            target = args.frames_dir / f'{label}-{index:04d}.png'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(args.video.resolve()),
                            '-vf', f'select=eq(n\\,{index})', '-frames:v', '1', str(target)], check=True)
            frames.append(str(target.resolve()))
    print(json.dumps({'file': str(args.video.resolve()), 'width': stream['width'],
                      'height': stream['height'], 'fps': fps, 'nominal_fps': nominal,
                      'duration': duration, 'decoded_frames': count,
                      'checks_passed': not errors, 'errors': errors, 'review_frames': frames},
                     ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == '__main__':
    main()
