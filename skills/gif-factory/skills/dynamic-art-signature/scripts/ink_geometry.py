"""Geometry-based defaults for signature rasters; no font-name presets.

These paths describe an ink reveal, not recovered calligraphic stroke order.
Only NumPy is required. Disconnected strokes use invisible pen-up links.
"""
from collections import deque
import heapq

import numpy as np


STEPS = [(dy, dx, float(np.hypot(dy, dx)))
         for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]


def components(mask):
    labels = np.zeros(mask.shape, np.int32)
    parts = []
    height, width = mask.shape
    for y, x in zip(*np.where(mask)):
        if labels[y, x]:
            continue
        label = len(parts) + 1
        labels[y, x] = label
        queue = deque([(int(y), int(x))])
        points = []
        while queue:
            py, px = queue.popleft()
            points.append((py, px))
            for dy, dx, _ in STEPS:
                qy, qx = py + dy, px + dx
                if (0 <= qy < height and 0 <= qx < width
                        and mask[qy, qx] and not labels[qy, qx]):
                    labels[qy, qx] = label
                    queue.append((qy, qx))
        parts.append(np.asarray(points, np.int32))
    return labels, parts


def stroke_profile(mask):
    """Estimate width at medial ridges with an integer city-distance transform."""
    ys, xs = np.where(mask)
    if not len(xs):
        return {"pixels": 0, "median_width_px": 0, "p90_width_px": 0}
    pad = np.pad(mask, 1)
    core = pad[1:-1, :-2] & pad[1:-1, 2:] & pad[:-2, 1:-1] & pad[2:, 1:-1]
    boundary = mask & ~core
    distance = np.zeros(mask.shape, np.int32)
    distance[boundary] = 1
    queue = deque(zip(*np.where(boundary)))
    height, width = mask.shape
    while queue:
        y, x = queue.popleft()
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if (0 <= ny < height and 0 <= nx < width
                    and mask[ny, nx] and not distance[ny, nx]):
                distance[ny, nx] = distance[y, x] + 1
                queue.append((ny, nx))
    dp = np.pad(distance, 1)
    ridge = mask.copy()
    for neighbor in [dp[:-2, 1:-1], dp[2:, 1:-1], dp[1:-1, :-2], dp[1:-1, 2:]]:
        ridge &= distance >= neighbor
    widths = 2 * distance[ridge] - 1
    return {
        "pixels": int(mask.sum()),
        "bounds_xyxy": [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)],
        "median_width_px": round(float(np.median(widths)), 2),
        "p90_width_px": round(float(np.percentile(widths, 90)), 2),
        "width_measure": "approximate medial city-distance width",
    }


def closest_points(a, b):
    """Memory-bounded nearest pair. Inputs and output coordinates are (y, x)."""
    best = (np.inf, None, None)
    for start in range(0, len(a), 192):
        block = a[start:start+192].astype(np.float64)
        for other in range(0, len(b), 2048):
            d = np.sum((block[:, None, :] - b[None, other:other+2048, :])**2, axis=2)
            ia, ib = np.unravel_index(np.argmin(d), d.shape)
            if d[ia, ib] < best[0]:
                best = (float(d[ia, ib]), tuple(a[start+ia]), tuple(b[other+ib]))
    return best[1], best[2], float(np.sqrt(best[0]))


def _walk(mask, start, bridges):
    height, width = mask.shape
    distance = np.full(mask.shape, np.inf)
    distance[start] = 0
    heap = [(0., int(start[0]), int(start[1]))]
    while heap:
        d, y, x = heapq.heappop(heap)
        if d > distance[y, x] + 1e-9:
            continue
        candidates = []
        for dy, dx, cost in STEPS:
            ny, nx = y+dy, x+dx
            if 0 <= ny < height and 0 <= nx < width and mask[ny, nx]:
                candidates.append(((ny, nx), cost))
        candidates.extend(bridges.get((y, x), []))
        for (ny, nx), cost in candidates:
            nd = d+cost
            if nd+1e-9 < distance[ny, nx]:
                distance[ny, nx] = nd
                heapq.heappush(heap, (nd, int(ny), int(nx)))
    return distance


def _sample_points(points, limit=800):
    if len(points) <= limit:
        return points
    return points[np.linspace(0, len(points)-1, limit, dtype=int)]


def ink_progress(mask, start_point=None, join_from=None):
    """Follow the current ink, including curves and returning hooks.

    Automatic starts use the earlier of two geodesic diameter endpoints.
    A tail can instead start nearest the body's endpoint. Explicit starts win.
    """
    labels, parts = components(mask)
    if not parts:
        raise ValueError("Cannot plan an empty ink layer")
    if len(parts) > 512:
        raise ValueError("Too many disconnected ink regions; clean the matte or split gestures")
    ys, xs = np.where(mask)
    if start_point is not None:
        requested = np.asarray(start_point, float)
        if requested.shape != (2,) or not np.isfinite(requested).all():
            raise ValueError("start_point must be a finite [x,y] pair")
        pick = int(np.argmin((xs-requested[0])**2+(ys-requested[1])**2))
        start = (int(ys[pick]), int(xs[pick]))
        source = "configured start"
    elif join_from is not None and join_from.any():
        near, _, _ = closest_points(np.column_stack((ys, xs)),
                                    _sample_points(np.column_stack(np.where(join_from)), 1200))
        start = near
        source = "nearest body join"
    else:
        largest = parts[int(np.argmax([len(p) for p in parts]))]
        start = tuple(largest[np.argmin(largest[:, 1]+.25*largest[:, 0])])
        source = "automatic ink endpoints"

    joined = {int(labels[start])-1}
    bridges = {}
    links = []
    samples = [_sample_points(p) for p in parts]
    nearest = {}
    newest = next(iter(joined))
    while len(joined) < len(parts):
        # Prim's frontier keeps each pair computation once, including dots and
        # fine disconnected flywhite. Do not repeatedly search the whole tree.
        for j in range(len(parts)):
            if j in joined:
                continue
            a, b, length = closest_points(samples[newest], samples[j])
            if j not in nearest or length < nearest[j][0]:
                nearest[j] = (length, a, b)
        j = min((j for j in nearest if j not in joined), key=lambda j: nearest[j][0])
        length, a, b = nearest[j]
        bridges.setdefault(a, []).append((b, length))
        bridges.setdefault(b, []).append((a, length))
        links.append(length)
        joined.add(j)
        newest = j
    distance = _walk(mask, start, bridges)
    if source == "automatic ink endpoints":
        a = tuple(np.unravel_index(np.argmax(np.where(mask, distance, -1)), mask.shape))
        from_a = _walk(mask, a, bridges)
        b = tuple(np.unravel_index(np.argmax(np.where(mask, from_a, -1)), mask.shape))
        start = min([a, b], key=lambda p: p[1]+.25*p[0])
        distance = from_a if start == a else _walk(mask, start, bridges)
    if not np.isfinite(distance[mask]).all():
        raise ValueError("Ink plan did not reach every pixel")
    progress = distance[mask]/max(float(distance[mask].max()), 1.)
    result = np.full(mask.shape, np.inf)
    result[mask] = progress
    report = {"method": "ink-geodesic", "start_source": source,
              "start_point": [int(start[1]), int(start[0])], "components": len(parts),
              "invisible_connector_lengths": [round(v, 2) for v in links], "coverage": 1.0}
    return result, report


def _path_samples(points):
    points = np.asarray(points, float)
    if (points.ndim != 2 or points.shape[1] != 2 or len(points) < 2
            or not np.isfinite(points).all()):
        raise ValueError("A pen path needs at least two finite [x,y] points")
    lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
    total = float(lengths.sum())
    if total <= 0:
        raise ValueError("Pen path length must be positive")
    samples, positions, walked = [], [], 0.
    for a, b, length in zip(points[:-1], points[1:], lengths):
        u = np.linspace(0, 1, max(2, int(length*2)), endpoint=False)
        samples.extend(a+(b-a)*u[:, None])
        positions.extend((walked+length*u)/total)
        walked += length
    samples = np.vstack([samples, points[-1]])
    positions = np.r_[positions, 1.]
    return samples, positions, total


def path_progress(mask, points):
    samples, positions, _ = _path_samples(points)
    ys, xs = np.where(mask)
    ink = np.column_stack((xs, ys))
    result = np.full(mask.shape, np.inf)
    max_error = 0.
    for start in range(0, len(ink), 256):
        d = np.sum((ink[start:start+256, None, :]-samples[None, :, :])**2, axis=2)
        nearest = np.argmin(d, axis=1)
        result[ys[start:start+len(d)], xs[start:start+len(d)]] = positions[nearest]
        max_error = max(max_error, float(np.sqrt(d[np.arange(len(d)), nearest]).max()))
    return result, {"method": "configured ink path", "coverage": 1.,
                    "path_error_px": round(max_error, 3)}


def ordered_pen_progress(mask, paths):
    """Reveal ink at first brush contact along authored, ordered pen strokes.

    Each raster pixel belongs to its nearest stroke. Within that stroke it is
    painted on the first nearby brush pass, so a crossing does not launch a new
    flood down every connected branch. Pen-up moves never touch the raster.
    """
    if not isinstance(paths, (list, tuple)) or not paths:
        raise ValueError('stroke_paths must contain at least one nonempty pen path')
    strokes = [_path_samples(points) for points in paths]
    lengths = np.asarray([stroke[2] for stroke in strokes])
    # Connected subpaths share a continuous pen; only real gaps cause a lift.
    lifts = np.asarray([
        np.linalg.norm(strokes[i-1][0][-1] - strokes[i][0][0]) > 1.5
        for i in range(1, len(strokes))
    ], dtype=bool)
    weights = lengths.copy()
    groups = np.r_[0, np.flatnonzero(lifts)+1, len(strokes)]
    for left, right in zip(groups[:-1], groups[1:]):
        # Give an isolated dot enough time for a visible tap.
        weights[left:right] *= max(1., lengths.sum() * .05 / weights[left:right].sum())
    gaps = lifts * lengths.sum() * .04
    total = float(weights.sum() + gaps.sum())
    starts = np.r_[0., np.cumsum(weights[:-1] + gaps)] / total
    spans = weights / total
    samples = np.vstack([stroke[0] for stroke in strokes])
    boundaries = np.r_[0, np.cumsum([len(stroke[0]) for stroke in strokes])]
    ys, xs = np.where(mask)
    ink = np.column_stack((xs, ys))
    radius = max(1.5, stroke_profile(mask)['p90_width_px'] / 2 + .75)
    result = np.full(mask.shape, np.inf)
    owners = np.empty(len(ink), dtype=np.int32)
    errors = np.empty(len(ink), dtype=np.float64)
    max_error = 0.
    for start in range(0, len(ink), 256):
        block = ink[start:start+256]
        distances = np.sum((block[:, None, :] - samples[None, :, :])**2, axis=2)
        nearest = np.column_stack([
            distances[:, boundaries[j]:boundaries[j+1]].min(axis=1)
            for j in range(len(strokes))
        ])
        owners[start:start+len(block)] = nearest.argmin(axis=1)
        errors[start:start+len(block)] = nearest.min(axis=1)
        max_error = max(max_error, float(np.sqrt(nearest.min(axis=1)).max()))
    radii = []
    for j, (stroke_samples, positions, _) in enumerate(strokes):
        selected = np.flatnonzero(owners == j)
        if not len(selected):
            radii.append(0.)
            continue
        owned_mask = np.zeros_like(mask)
        owned_mask[ys[selected], xs[selected]] = True
        # Thin upstrokes must not use the brush width of a later broad downstroke.
        stroke_radius = max(1.25, stroke_profile(owned_mask)['p90_width_px'] / 2 + .5)
        radii.append(round(stroke_radius, 3))
        for start in range(0, len(selected), 256):
            indices = selected[start:start+256]
            local = np.sum((ink[indices, None, :] - stroke_samples[None, :, :])**2, axis=2)
            support = np.maximum(stroke_radius**2, errors[indices] + .25)
            first_touch = (local <= support[:, None]).argmax(axis=1)
            values = starts[j] + spans[j] * positions[first_touch]
            result[ys[indices], xs[indices]] = values
    if max_error > max(12 * mask.shape[1] / 960, radius * 3):
        raise ValueError('stroke_paths miss part of the ink; trace this artwork again')
    return result, {'method': 'ordered-pen', 'coverage': 1.,
                    'stroke_count': len(strokes), 'pen_up_links': int(lifts.sum()),
                    'stroke_pen_radii_px': radii,
                    'path_error_px': round(max_error, 3)}


def reveal_times(mask, start, end, *, pen=None, join_from=None, path=None, slowing=False):
    pen = pen or {}
    front = float(pen.get("front_duration", min(.006, (end-start)*.025)))
    power = float(pen.get("acceleration_power", 1.3))
    if not 0 < front < end-start or not np.isfinite(power) or power <= 0:
        raise ValueError("Pen duration, front_duration and acceleration_power must be positive")
    if 'stroke_paths' in pen:
        if path is not None:
            raise ValueError('Use stroke_paths or a single path, not both')
        progress, report = ordered_pen_progress(mask, pen['stroke_paths'])
    else:
        progress, report = (path_progress(mask, path) if path is not None else
                            ink_progress(mask, pen.get("start_point"), join_from))
    values = np.clip(progress[mask], 0, 1)
    values = 1-np.sqrt(1-values) if slowing else values**(1/power)
    times = np.full(mask.shape, np.inf)
    times[mask] = start+(end-start-front)*values
    report.update({"start_seconds": start, "end_seconds": end,
                   "duration_seconds": round(end-start, 6), "front_duration": front})
    return times, front, report


def fragment_defaults(profile, width, timing):
    scale = width/960.
    stroke = profile["median_width_px"]/scale
    # Thin hairlines keep longer intact pieces and smaller movement.
    cw = max(8, round(np.clip(48/(1+stroke/12), 24, 48)*scale))
    thin = stroke <= 5
    return {"cell_width": cw, "cell_height": max(5, round(cw*.65)),
            "rotation": 20 if thin else 32, "drift": width*(.020 if thin else .027),
            "alpha_power": 1.75, "edge_softness": 2.3,
            "birth_base": timing["first_start"]+.10, "birth_spread": .19,
            "land_base": timing["first_end"]+.18, "land_spread": .34,
            "time_jitter": .045}
