#!/usr/bin/env python3
"""Inspect a video, optional cover and ZIP without changing input media or using the network."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


def probe(path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def inspect(args):
    if not shutil.which('ffprobe'):
        raise ValueError('ffprobe is required; install FFmpeg before inspecting media.')
    path = args.video.resolve()
    data = probe(path)
    video = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
    if video is None:
        raise ValueError('No video stream.')
    fps = float(Fraction(video['avg_frame_rate']))
    duration = float(video.get('duration', data['format']['duration']))
    size = [video['width'], video['height']]
    if size != [args.width, args.height]:
        raise ValueError(f'Wrong dimensions: {size}; expected {[args.width, args.height]}.')
    if abs(fps - args.fps) > 0.001:
        raise ValueError(f'Wrong fps: {fps}; expected {args.fps}.')
    if args.duration is not None and abs(duration - args.duration) > 0.05:
        raise ValueError(f'Wrong duration: {duration}; expected {args.duration}.')
    frames = int(video['nb_frames']) if video.get('nb_frames', 'N/A') != 'N/A' else None
    if frames is not None and abs(frames - round(duration * fps)) > 1:
        raise ValueError('Frame count and stream duration do not agree.')
    if frames is not None and args.duration is not None and frames != round(args.duration * args.fps):
        raise ValueError('Frame count differs from the requested timeline length.')
    audio = [s for s in data['streams'] if s['codec_type'] == 'audio']
    if not audio and not args.allow_silent:
        raise ValueError('No audio stream; use --allow-silent only for an intended silent video.')
    report = {
        'ok': True, 'file': str(path), 'dimensions': size, 'fps': fps,
        'duration': duration, 'frames': frames, 'video_codec': video['codec_name'],
        'audio_codecs': [s['codec_name'] for s in audio],
        'full_decode': False, 'visual_review': 'not assessed', 'listening_review': 'not assessed',
    }
    if args.full_decode:
        if not shutil.which('ffmpeg'):
            raise ValueError('ffmpeg is required for --full-decode.')
        decoded = subprocess.run(
            ['ffmpeg', '-hide_banner', '-v', 'error', '-xerror', '-i', str(path), '-f', 'null', '-'],
            capture_output=True, text=True, check=True,
        )
        if decoded.stderr.strip():
            raise ValueError(f'Decoder reported errors: {decoded.stderr.strip()}')
        report['full_decode'] = True
    if args.cover:
        streams = probe(args.cover.resolve())['streams']
        cover = next((s for s in streams if s['codec_type'] == 'video'), None)
        if cover is None or [cover['width'], cover['height']] != size:
            raise ValueError('Cover dimensions differ from video dimensions.')
        report['cover'] = {'file': str(args.cover.resolve()), 'dimensions': size}
    if args.archive:
        with zipfile.ZipFile(args.archive) as archive:
            bad = archive.testzip()
            members = archive.infolist()
            if bad or not members:
                raise ValueError(f'Invalid or empty project archive: {bad}')
            if any(not m.is_dir() and m.file_size == 0 for m in members):
                raise ValueError('Project archive contains an empty file.')
            report['archive'] = {'file': str(args.archive.resolve()), 'members': len(members), 'crc': 'pass'}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--fps', type=float, default=30)
    parser.add_argument('--width', type=int, default=1080)
    parser.add_argument('--height', type=int, default=1920)
    parser.add_argument('--duration', type=float)
    parser.add_argument('--cover', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--full-decode', action='store_true')
    parser.add_argument('--allow-silent', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    try:
        report = inspect(args)
    except (ValueError, OSError, subprocess.CalledProcessError, zipfile.BadZipFile, KeyError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding='utf-8')
    print(payload, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
