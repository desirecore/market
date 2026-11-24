#!/usr/bin/env python3
"""Lay out three photographs and their existing title artwork as a portrait PNG."""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageOps

PANEL_WIDTH = 1536
PANEL_HEIGHT = 644
GUTTER = 32


def open_image(path):
    with Image.open(path) as source:
        return ImageOps.exif_transpose(source).copy()


def remove_neutral_gray(image):
    """Extract letterforms from artwork already on a plain gray field."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    edge = max(1, rgb.shape[1] // 40)
    samples = np.concatenate((rgb[:, :edge], rgb[:, -edge:]), axis=1)
    gray = np.median(samples, axis=1)[:, None, :]
    delta = rgb - gray
    opacity = np.clip((np.max(np.abs(delta), axis=2) - 10) / 23, 0, 1)
    color = np.clip(gray + delta / np.maximum(opacity[:, :, None], 0.15), 0, 255)
    art = Image.fromarray(np.uint8(color))
    art.putalpha(Image.fromarray(np.uint8(opacity * 255)))
    return art


def load_title(path, panel):
    art = open_image(path).convert("RGBA")
    if "title_crop" in panel:
        left, top, right, bottom = panel["title_crop"]
        if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
            raise ValueError("title_crop must be [left, top, right, bottom] within 0–1")
        art = art.crop((
            round(left * art.width), round(top * art.height),
            round(right * art.width), round(bottom * art.height),
        ))
    if panel.get("title_matte", "alpha") == "gray":
        art = remove_neutral_gray(art)
    elif art.getchannel("A").getextrema()[0] == 255:
        raise ValueError(f"{path} is opaque. Supply a transparent title or use title_matte: gray.")
    bounds = art.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError(f"No visible lettering in {path}")
    return art.crop(bounds)


def pair(panel, name, default, allow_zero=True):
    values = panel.get(name, default)
    if len(values) != 2 or not all(0 <= value <= 1 for value in values):
        raise ValueError(f"{name} must contain two numbers within 0–1")
    if not allow_zero and min(values) == 0:
        raise ValueError(f"{name} values must be greater than zero")
    return values


def render_panel(root, panel):
    photo = ImageOps.fit(
        open_image(root / panel["photo"]).convert("RGB"),
        (PANEL_WIDTH, PANEL_HEIGHT), Image.Resampling.LANCZOS,
        centering=tuple(pair(panel, "photo_focus", (0.5, 0.5))),
    )
    photo = ImageEnhance.Color(photo).enhance(panel.get("saturation", 1.0))
    photo = ImageEnhance.Brightness(photo).enhance(panel.get("exposure", 1.0))
    title = load_title(root / panel["title"], panel)
    max_width, max_height = pair(panel, "title_max", (0.65, 0.72), allow_zero=False)
    title.thumbnail(
        (max(1, round(max_width * PANEL_WIDTH)), max(1, round(max_height * PANEL_HEIGHT))),
        Image.Resampling.LANCZOS,
    )
    center_x, center_y = pair(panel, "title_center", (0.5, 0.5))
    x = round(center_x * PANEL_WIDTH - title.width / 2)
    y = round(center_y * PANEL_HEIGHT - title.height / 2)
    if min(x, y) < 0 or x + title.width > PANEL_WIDTH or y + title.height > PANEL_HEIGHT:
        raise ValueError(f"Title exceeds panel bounds: {panel['title']}")
    photo.paste(title, (x, y), title.getchannel("A"))
    return photo


def render(config_path, output_path):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    panels = config["panels"]
    if len(panels) != 3:
        raise ValueError("A portrait sheet requires three panels, in top-to-bottom order")
    canvas = Image.new(
        "RGB", (PANEL_WIDTH + GUTTER * 2, PANEL_HEIGHT * 3 + GUTTER * 4), "#fafaf8",
    )
    for index, panel in enumerate(panels):
        artwork = render_panel(config_path.parent, panel)
        canvas.paste(artwork, (GUTTER, GUTTER + index * (PANEL_HEIGHT + GUTTER)))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="JSON file with the three panels")
    parser.add_argument("--out", type=Path, required=True, help="Destination PNG")
    args = parser.parse_args()
    render(args.config, args.out)
