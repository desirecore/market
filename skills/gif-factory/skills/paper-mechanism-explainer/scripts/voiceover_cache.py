#!/usr/bin/env python3
"""Look up or record Clipchamp narration in a local cache; never uses the network."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def digest(path):
    checksum = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            checksum.update(block)
    return checksum.hexdigest()


def request_for(text_path, profile_path):
    text = text_path.read_text(encoding='utf-8-sig')
    if not text.strip():
        raise ValueError('Narration text is empty.')
    profile = json.loads(profile_path.read_text(encoding='utf-8-sig'))
    if not isinstance(profile, dict) or profile.get('provider') != 'clipchamp':
        raise ValueError('A Clipchamp voice profile is required.')
    settings = {'provider': 'clipchamp'}
    for field in ('language', 'voice', 'pitch'):
        value = profile.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'Missing or invalid profile field: {field}')
        settings[field] = value
    speed = profile.get('speed')
    if isinstance(speed, bool) or not isinstance(speed, (int, float)):
        raise ValueError('Profile speed must be a number between 0.5 and 2.')
    if not math.isfinite(speed) or not 0.5 <= speed <= 2:
        raise ValueError('Profile speed must be between 0.5 and 2.')
    settings['speed'] = float(speed)
    request = {'schema': 1, 'text': text, 'profile': settings}
    serialized = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return request, hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def lookup(entry, request, key):
    result = {'status': 'miss', 'request_sha256': key, 'entry': str(entry)}
    manifest_path = entry / 'manifest.json'
    if not manifest_path.is_file():
        return result
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest['request_sha256'] != key or manifest['request'] != request:
            raise ValueError('Cached request does not match.')
        audio_name = manifest['audio']['file']
        if audio_name not in ('narration.mp3', 'narration.m4a', 'narration.wav', 'narration.ogg'):
            raise ValueError('Invalid cached audio filename.')
        audio = entry / audio_name
        if not audio.is_file() or digest(audio) != manifest['audio']['sha256']:
            raise ValueError('Cached audio is missing or its checksum changed.')
        result.update(status='hit', audio=str(audio), duration=manifest['audio']['duration'])
    except (OSError, ValueError, KeyError, TypeError) as error:
        result['reason'] = str(error)
    return result


def audio_duration(path):
    for program in ('ffprobe', 'ffmpeg'):
        if not shutil.which(program):
            raise ValueError(f'{program} is required to record verified audio.')
    probe = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(probe.stdout)
    if not any(stream.get('codec_type') == 'audio' for stream in data['streams']):
        raise ValueError('No audio stream.')
    duration = float(data['format']['duration'])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Audio duration must be positive.')
    subprocess.run(
        ['ffmpeg', '-hide_banner', '-nostdin', '-v', 'error', '-xerror', '-i', str(path),
         '-map', '0:a:0', '-f', 'null', '-'],
        capture_output=True, text=True, check=True,
    )
    return duration


def record(entry, request, key, audio):
    suffix = audio.suffix.lower()
    if suffix not in ('.mp3', '.m4a', '.wav', '.ogg'):
        raise ValueError('Record an MP3, M4A, WAV or OGG audio file.')
    if entry.exists():
        raise ValueError('Cache entry already exists; reuse it or choose a new cache directory for a new take.')
    entry.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.voiceover-', dir=entry.parent) as temporary:
        stage = Path(temporary)
        target = stage / ('narration' + suffix)
        shutil.copyfile(audio, target)
        duration = audio_duration(target)
        manifest = {
            'request_sha256': key,
            'request': request,
            'audio': {'file': target.name, 'sha256': digest(target), 'duration': duration},
            'full_decode': True,
            'voice_identity_review': 'caller must verify the selected voice in Clipchamp',
            'listening_review': 'not assessed by this tool',
        }
        (stage / 'manifest.json').write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8',
        )
        stage.rename(entry)
    return lookup(entry, request, key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('lookup', 'record'))
    parser.add_argument('--text', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--audio', type=Path)
    args = parser.parse_args()
    try:
        request, key = request_for(args.text, args.profile)
        entry = args.cache_dir.resolve() / key
        if args.command == 'record':
            if not args.audio:
                raise ValueError('--audio is required for record.')
            report = record(entry, request, key, args.audio.resolve())
        else:
            report = lookup(entry, request, key)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(json.dumps({'status': 'error', 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
