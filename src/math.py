"""
=============================================================================
 math.py  –  Geometric helpers for mouse-drawing interpolation
=============================================================================

When the user drags the mouse quickly, pygame only reports the start and
end positions – it doesn't fire an event for every pixel in between.
Without interpolation this would leave gaps in the drawn line.

The ``interpolate`` function walks from the previous cursor position to
the current one in fixed-size steps (``CELL_SIZE`` pixels) and returns
every point along the way so the caller can activate those grid cells.
=============================================================================
"""

from __future__ import annotations

import math

from .options import CELL_DELTA


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx * dx + dy * dy)


def interpolate(
    x: float, y: float, prev_x: float, prev_y: float
) -> list[tuple[float, float]]:
    distance = euclidean_distance(x, y, prev_x, prev_y)

    if distance < 1.0:
        return []

    # Unit direction vector from prev → current.
    dx = x - prev_x
    dy = y - prev_y
    cos_a = dx / distance
    sin_a = dy / distance

    step = float(CELL_DELTA)
    steps = int(distance / step)

    points: list[tuple[float, float]] = []
    walk_x, walk_y = prev_x, prev_y

    for _ in range(steps):
        points.append((walk_x, walk_y))
        walk_x += cos_a * step
        walk_y += sin_a * step

    return points
