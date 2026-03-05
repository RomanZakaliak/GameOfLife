import math

import numba as nb

from .options import CELL_SIZE


@nb.njit(fastmath=True)
def get_euclidean_distance(x1, y1, x2, y2):
    return int(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))


def interpolate(x, y, prev_x, prev_y):
    angle = math.pi + math.atan2(prev_y - y, prev_x - x)
    angle_sin = math.sin(angle)
    angle_cos = math.cos(angle)

    distance = get_euclidean_distance(x, y, prev_x, prev_y)

    interpolations = []
    prev_x_l, prev_y_l = prev_x, prev_y
    for _ in range(0, distance // CELL_SIZE):
        interpolations.append((prev_x_l, prev_y_l))

        prev_x_l, prev_y_l = (
            prev_x_l + angle_cos * CELL_SIZE,
            prev_y_l + angle_sin * CELL_SIZE,
        )

    return interpolations
