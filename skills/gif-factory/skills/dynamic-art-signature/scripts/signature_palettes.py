"""Fixed color fields for signature ink, independent of the writing timeline."""

import numpy as np
from PIL import Image, ImageColor, ImageFilter


# Each preset defines the backdrop, color placement, and ink colors in order.
PALETTES = {
    'macaron': ('#20202A', 'gradient', ('#F6B6C9', '#CDB9F6', '#9DE2CF')),
    'cola-red': ('#C41D30', 'bands', ('#FFF3DE',)),
    'hello-split': ('#191B24', 'diagonal', ('#FF7897', '#FFC569', '#83C4FF', '#BAA4FF')),
    'google-color': ('#151920', 'bands', ('#5B94FF', '#FF6C63', '#FBD152', '#5B94FF', '#69C98A')),
    'sea-salt-soda': ('#132B35', 'gradient', ('#6AD3EE', '#D9F689')),
    'retro-print': ('#F5E8D4', 'bands', ('#AE342A', '#283F64')),
    'night-gradient': ('#151126', 'gradient', ('#60C4FF', '#8379FF', '#F372D0')),
}


def _ink_opacity(source, ink, source_background):
    """Keep real alpha, or estimate flattened RGB coverage from local contrast.

    Flattened artwork has no recoverable exact alpha. Nearby stronger ink gives
    the local foreground contrast, so antialiasing and flywhite stay softer than
    the stroke interior without treating every covered pixel as opaque.
    """
    alpha = np.asarray(source.getchannel('A'))
    if np.any(alpha < 255):
        return alpha

    rgb = np.asarray(source.convert('RGB'), dtype=np.float32)
    contrast = np.max(np.abs(rgb - np.asarray(source_background, dtype=np.float32)), axis=2)
    contrast = np.where(ink, contrast, 0).astype(np.uint8)
    radius = min(15, max(3, round(max(source.size) / 64)))
    local_ink = np.asarray(Image.fromarray(contrast).filter(
        ImageFilter.MaxFilter(radius * 2 + 1)), dtype=np.float32)
    coverage = np.divide(contrast, local_ink, out=np.zeros_like(local_ink), where=local_ink > 0)
    return np.rint(np.clip(coverage, 0, 1) * 255).astype(np.uint8)


def apply_palette(name, source, ink, source_background):
    """Composite a preset while retaining source alpha or estimated RGB edges."""
    if not isinstance(name, str) or name not in PALETTES:
        raise ValueError(f'Unknown signature palette {name!r}. Choose from {", ".join(PALETTES)}')

    backdrop, placement, swatches = PALETTES[name]
    background = ImageColor.getrgb(backdrop)
    colors = np.array([ImageColor.getrgb(swatch) for swatch in swatches], dtype=np.uint8)
    ys, xs = np.nonzero(ink)
    projection = xs + .25 * ys if placement == 'diagonal' else xs
    positions = (projection - projection.min()) / max(1, np.ptp(projection))
    if placement == 'gradient':
        stops = np.linspace(0, 1, len(colors))
        ink_rgb = np.rint(np.column_stack([
            np.interp(positions, stops, channel) for channel in colors.T
        ])).astype(np.uint8)
    elif len(colors) == 1:
        ink_rgb = colors[0]
    else:
        # Blend around each boundary while preserving the center of each band.
        band_positions = positions * len(colors)
        boundary = np.clip(np.floor(band_positions + .5).astype(int), 1, len(colors) - 1)
        blend = np.clip((band_positions - boundary) / .62 + .5, 0, 1)[:, None]
        blend = blend * blend * (3 - 2 * blend)
        ink_rgb = np.rint(colors[boundary - 1] * (1 - blend) + colors[boundary] * blend).astype(np.uint8)

    pixels = np.zeros((source.height, source.width, 4), dtype=np.uint8)
    pixels[ys, xs, :3] = ink_rgb
    pixels[ys, xs, 3] = _ink_opacity(source, ink, source_background)[ys, xs]
    art = Image.alpha_composite(
        Image.new('RGBA', source.size, (*background, 255)), Image.fromarray(pixels)
    )
    return background, art.convert('RGB')
