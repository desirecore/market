#!/usr/bin/env python3
"""Render a two-gesture signature with particles that settle into selected ink."""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw


FPS = 60
DURATION = 4
UPPER_START, UPPER_END = 0.30, 0.44
LOWER_START, BODY_END, TAIL_END = 1.46, 1.64, 2.36
SETTLE_START, SETTLE_END = 1.80, 2.25
FADE_START = 3.70


def ramp(now, start, end):
    return np.clip((now - start) / (end - start), 0, 1)


def particle_plan(target, effect, seed):
    """Select actual ink pixels as landing points and time each local deposit."""
    rng = np.random.default_rng(seed)
    ys, xs = np.where(target)
    picks = rng.choice(len(xs), size=min(380, len(xs)), replace=False)
    x, y = xs[picks], ys[picks]
    horizontal = (x - xs.min()) / max(1, np.ptp(xs))
    vertical = (y - ys.min()) / max(1, np.ptp(ys))
    order = vertical if effect == "rain" else horizontal
    land = SETTLE_START + 0.34 * order + rng.uniform(0, 0.10, len(x))
    if effect == "rain":
        origin_x = x + rng.uniform(4, 20, len(x))
        origin_y = y - rng.uniform(38, 88, len(x))
    else:
        origin_x = x + rng.uniform(-56, 56, len(x))
        origin_y = y + rng.uniform(-58, 30, len(x))

    # Expand each arrival into adjacent ink. Sparse details fill by the end.
    arrival = np.full(target.shape, SETTLE_END, dtype=np.float32)
    height, width = target.shape
    radius = 13
    for px, py, time in zip(x, y, land):
        left, right = max(0, px - radius), min(width, px + radius + 1)
        top, bottom = max(0, py - radius), min(height, py + radius + 1)
        yy, xx = np.ogrid[top:bottom, left:right]
        distance = np.hypot(xx - px, yy - py)
        region = arrival[top:bottom, left:right]
        np.minimum(region, time + 0.006 * distance, out=region, where=distance <= radius)
    return arrival, (x, y, origin_x, origin_y, land)


def draw_particles(frame, plan, effect, now):
    x, y, origin_x, origin_y, land = plan
    progress = ramp(now, land - 0.32, land)
    active = (progress > 0) & (progress < 1)
    draw = ImageDraw.Draw(frame, "RGBA")
    for index in np.flatnonzero(active):
        t = progress[index]
        ease = t ** 1.6 if effect == "rain" else 1 - (1 - t) ** 2
        px = origin_x[index] + (x[index] - origin_x[index]) * ease
        py = origin_y[index] + (y[index] - origin_y[index]) * ease
        alpha = int(215 * min(1, t * 4, (1 - t) * 6))
        if effect == "rain":
            draw.line((px + 1, py - 5, px, py), (171, 190, 255, alpha), width=1)
        elif index % 7 == 0:
            draw.line((px - 2, py, px + 2, py), (255, 228, 250, alpha))
            draw.line((px, py - 2, px, py + 2), (255, 228, 250, alpha))
        else:
            draw.point((px, py), (255, 228, 250, alpha))


def horizontal_reveal(mask, progress):
    occupied = np.flatnonzero(mask.any(axis=0))
    left, right = occupied[0], occupied[-1] + 1
    position = left + (right - left) * progress
    return mask * np.clip(position - np.arange(mask.shape[1]), 0, 1)


def render(config_path, out):
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    effect = cfg["particle"]
    if effect not in {"rain", "stardust"}:
        raise ValueError("particle must be rain or stardust")

    art = Image.open(config_path.parent / cfg["art"]).convert("RGB")
    matte = Image.open(config_path.parent / cfg["upper_mask"]).convert("L")
    width, height = art.size
    if matte.size != art.size or width % 2 or height % 2:
        raise ValueError("Art and upper mask must have matching, even dimensions")

    ink = np.asarray(art).astype(np.float32)
    background = np.asarray(cfg["background"], dtype=np.float32)
    # The supplied plates are decoded RGB frames. Remove small codec/background variations.
    strength = np.max(np.abs(ink - background), axis=2)
    ink_alpha = np.clip((strength - 7) / 12, 0, 1)
    upper = np.asarray(matte) > 0
    region = Image.new("L", art.size)
    ImageDraw.Draw(region).polygon([tuple(point) for point in cfg["target_polygon"]], fill=255)
    selected = np.asarray(region) > 0
    target = selected & ~upper & (ink_alpha > 0)
    body = ~upper & ~selected & (ink_alpha > 0)
    if not all(mask.any() for mask in (upper, body, target)):
        raise ValueError("Upper, body and particle target must each contain ink")
    arrival, plan = particle_plan(target, effect, cfg["seed"])

    out.parent.mkdir(parents=True, exist_ok=True)
    video = out.with_suffix(".mp4")
    ffmpeg = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    command = [
        *ffmpeg, "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
        "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-crf", "16",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video),
    ]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        with encoder.stdin as frames:
            for index in range(FPS * DURATION):
                now = index / FPS
                top = horizontal_reveal(upper, ramp(now, UPPER_START, UPPER_END) ** 1.3)
                fast = 0.78 * ramp(now, LOWER_START, BODY_END) ** 1.3
                tail = 0.22 * (1 - (1 - ramp(now, BODY_END, TAIL_END)) ** 2)
                rest = horizontal_reveal(body, fast + tail)
                deposit = target * ramp(now, arrival, arrival + 0.06)
                visible = np.maximum(np.maximum(top, rest), deposit)
                alpha = ink_alpha * visible * (1 - ramp(now, FADE_START, DURATION))
                rgb = background + (ink - background) * alpha[:, :, None]
                frame = Image.fromarray(np.rint(rgb).astype(np.uint8))
                if LOWER_START < now < SETTLE_END:
                    draw_particles(frame, plan, effect, now)
                frames.write(frame.tobytes())
        if encoder.wait() != 0:
            raise RuntimeError("FFmpeg could not encode the signature")

    palette = "[0:v]fps=25,split[a][b];[a]palettegen[p];[b][p]paletteuse"
    subprocess.run(
        [*ffmpeg, "-i", str(video), "-filter_complex", palette, "-loop", "0",
         str(out.with_suffix(".gif"))], check=True,
    )
    subprocess.run(
        [*ffmpeg, "-ss", "2.7", "-i", str(video), "-frames:v", "1",
         str(out.with_suffix(".png"))], check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="Output basename without extension")
    args = parser.parse_args()
    render(args.config, args.out)
