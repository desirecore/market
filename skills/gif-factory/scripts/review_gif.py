#!/usr/bin/env python3
"""Extract the delivered GIF for visual review; bind sign-off to its exact hash.

Image metrics are review hints, never an automatic aesthetic pass.
"""
import argparse
import hashlib
import json
from pathlib import Path
from shutil import copyfile
from statistics import median

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageSequence, ImageStat


def audit(path, output, focus=None):
    output.mkdir(parents=True, exist_ok=True)
    frames, durations, boxes = [], [], []
    errors = []
    with Image.open(path) as gif:
        size, loop = gif.size, gif.info.get('loop')
        for frame in ImageSequence.Iterator(gif):
            rgba = frame.convert('RGBA')
            frames.append(rgba)
            durations.append(frame.info.get('duration', 0))
            boxes.append(rgba.getchannel('A').getbbox())
    if not frames:
        raise ValueError('Empty animation')
    if loop != 0:
        errors.append('loop must be 0')
    if any(ms <= 0 for ms in durations):
        errors.append('nonpositive frame delay')
    for i, (frame, box) in enumerate(zip(frames, boxes)):
        alpha = frame.getchannel('A')
        if alpha.getextrema() != (0, 255):
            errors.append(f'frame {i}: expected transparent and opaque pixels')
        if not box or not (0 < box[0] < box[2] < size[0] and 0 < box[1] < box[3] < size[1]):
            errors.append(f'frame {i}: blank or touches canvas edge')
    distinct = len({hashlib.sha256(f.tobytes()).hexdigest() for f in frames})
    if distinct < 2:
        errors.append('no visible frame changes')
    if focus and not (0 <= focus[0] < focus[2] <= size[0] and 0 <= focus[1] < focus[3] <= size[1]):
        raise ValueError('Focus box must be inside the GIF')
    # Native-size frames: do not shrink these to hide small facial defects.
    columns = min(4, len(frames))
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new('RGB', (columns*size[0], rows*(size[1]+28)), '#eff2f5')
    pen = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    opaque = []
    focus_sheet = None
    if focus:
        fw, fh = focus[2]-focus[0], focus[3]-focus[1]
        focus_sheet = Image.new('RGB', (fw*columns, (fh+28)*rows), '#eff2f5')
    for i, (frame, ms) in enumerate(zip(frames, durations)):
        frame.save(output/f'frame-{i:03d}.png')
        x, y = i % columns*size[0], i // columns*(size[1]+28)
        sheet.paste(frame, (x, y+28), frame)
        pen.text((x+8, y+8), f'{i:02d}  {ms}ms', font=font, fill='#303443')
        matte = Image.new('RGB', size, '#eff2f5')
        matte.paste(frame, (0, 0), frame)
        opaque.append(matte)
        if focus_sheet:
            crop = matte.crop(focus)
            fx, fy = i % columns*fw, i // columns*(fh+28)
            focus_sheet.paste(crop, (fx, fy+28))
            ImageDraw.Draw(focus_sheet).text((fx+8, fy+8), str(i), font=font, fill='#303443')
    sheet.save(output/'frames.png')
    if focus_sheet:
        focus_sheet.save(output/'focus.png')
    changes = []
    for i, current in enumerate(opaque):
        previous = opaque[i-1]  # index 0 includes the loop seam
        diff = ImageChops.difference(current, previous)
        if focus:
            diff = diff.crop(focus)
        changes.append(sum(ImageStat.Stat(diff).mean)/(3*255))
    typical = median(changes)
    candidates = [i for i, value in enumerate(changes) if value > max(.04, typical*2.5)]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    report = dict(gif=path.name, sha256=digest, size=size, decoded_frames=len(frames),
                  distinct_frames=distinct, loop_ms=sum(durations), durations_ms=durations,
                  technical_status='failed' if errors else 'passed', errors=errors,
                  transition_change=changes, transition_candidates=candidates,
                  warning='Transition scores are hints. Blinks can score high; ugly faces can score low. Visual review is required.')
    (output/'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    review_path = output/'review.json'
    # Re-running after a repair must not silently preserve stale approval.
    existing = json.loads(review_path.read_text()) if review_path.exists() else {}
    if existing.get('sha256') != digest:
        template = dict(sha256=digest, reviewer=None,
                        frames=[dict(index=i, decision='pending', issues=[]) for i in range(len(frames))],
                        playback='pending', loop_seam='pending', user_acceptance='pending')
        review_path.write_text(json.dumps(template, ensure_ascii=False, indent=2))
    copyfile(path, output/'animation.gif')
    # Browser player uses the final decoded PNGs and their actual delays, plus the actual GIF.
    player = '''<!doctype html><meta charset="utf-8"><title>GIF review</title>
<style>body{font:18px system-ui;background:#eff2f5;color:#303443}img{max-width:46vw;vertical-align:top}button{font-size:18px;margin:8px}</style>
<h1>Delivered GIF / decoded frame</h1><p id="status"></p>
<button onclick="playing=!playing">Play / pause</button><button onclick="playing=false;step(-1)">Previous</button><button onclick="playing=false;step(1)">Next</button>
<p><img src="animation.gif"><img id="frame"></p>
<p>Inspect every face, hand, costume and transition; first/last transition is part of the review.</p>
<script>const delays=DELAYS;let index=0,playing=true;function draw(){document.getElementById('frame').src='frame-'+String(index).padStart(3,'0')+'.png';document.getElementById('status').textContent='Frame '+index+' / '+(delays.length-1)+' — '+delays[index]+' ms';}function step(d){index=(index+d+delays.length)%delays.length;draw();}function tick(){if(playing)step(1);setTimeout(tick,delays[index]);}draw();setTimeout(tick,delays[0]);</script>'''.replace('DELAYS', json.dumps(durations))
    (output/'index.html').write_text(player)
    return report


def check_review(audit_path, review_path, gif_path=None):
    report = json.loads(audit_path.read_text())
    review = json.loads(review_path.read_text())
    expected = list(range(report['decoded_frames']))
    rows = review.get('frames', [])
    if report['technical_status'] != 'passed':
        raise ValueError('Technical audit failed')
    if review.get('sha256') != report['sha256']:
        raise ValueError('Review belongs to a different GIF revision')
    actual = gif_path or audit_path.parent/'animation.gif'
    if hashlib.sha256(actual.read_bytes()).hexdigest() != report['sha256']:
        raise ValueError('GIF changed after extraction; re-extract and re-review')
    if sorted(row.get('index', -1) for row in rows) != expected:
        raise ValueError('Review must cover every decoded frame exactly once')
    if not review.get('reviewer') or any(row.get('decision') != 'pass' for row in rows):
        raise ValueError('Visual review is incomplete or contains a rejected frame')
    if review.get('playback') != 'pass' or review.get('loop_seam') != 'pass':
        raise ValueError('Playback and loop seam need explicit visual review')
    return dict(technical_status='passed', visual_status='reviewed', reviewer=review['reviewer'],
                user_acceptance=review.get('user_acceptance', 'pending'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    extract = sub.add_parser('extract')
    extract.add_argument('gif', type=Path)
    extract.add_argument('output', type=Path)
    extract.add_argument('--focus', nargs=4, type=int, metavar=('LEFT', 'TOP', 'RIGHT', 'BOTTOM'))
    check = sub.add_parser('check')
    check.add_argument('audit', type=Path)
    check.add_argument('review', type=Path)
    check.add_argument('--gif', type=Path, help='Final GIF to verify; defaults to extracted animation.gif')
    args = parser.parse_args()
    if args.command == 'extract':
        result = audit(args.gif, args.output, args.focus)
        print(json.dumps({k: result[k] for k in ['technical_status', 'decoded_frames', 'loop_ms', 'transition_candidates']}))
        if result['errors']:
            raise SystemExit(1)
    else:
        try:
            print(json.dumps(check_review(args.audit, args.review, args.gif)))
        except ValueError as error:
            parser.exit(2, str(error)+'\n')


if __name__ == '__main__':
    main()
