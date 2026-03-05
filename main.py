import math
import random
import traceback

import numba as nb
import numpy as np
import pygame

from src import options as op
from src.cell_shape import CellShape, LineShape, PoligonShape, PoligonShapeAdapter
from src.event_handlers import on_game_pause
from src.math import interpolate

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


@nb.njit
def init_matrix(fill_random: bool, rows, cols):
    if fill_random:
        return np.random.randint(0, 2, size=(rows, cols))

    return np.zeros((rows, cols), dtype=nb.int64)


@nb.jit(forceobj=True, looplift=False, parallel=True)
def draw_matrix(game_matrix, shape: CellShape, line_shape: LineShape) -> None:
    for row in nb.prange(op.V_RES):
        for col in nb.prange(op.H_RES):
            if row >= len(game_matrix) or col >= len(game_matrix[0]):
                continue
            if game_matrix[row][col] == 1:
                shape.draw([col * op.RESOLUTION, row * op.RESOLUTION], op.CELL_SIZE)

                if line_shape is None:
                    return

                for i in nb.prange(-1, 2):
                    for j in nb.prange(-1, 2):
                        row_index = row + i
                        col_index = col + j

                        if (
                            row_index >= len(game_matrix)
                            or col_index >= len(game_matrix[0])
                            or game_matrix[row_index][col_index] == 0
                        ):
                            continue

                        line_shape.draw(
                            [col * op.RESOLUTION, row * op.RESOLUTION],
                            [col_index * op.RESOLUTION, row_index * op.RESOLUTION],
                        )


@nb.jit(fastmath=True, parallel=True)
def count_cell_neighbors(game_matrix, row: int, col: int) -> int:
    sum = 0
    for i in nb.prange(-1, 2):
        for j in nb.prange(-1, 2):
            row_index = (row + i) % op.V_RES
            col_index = (col + j) % op.H_RES

            if row_index >= len(game_matrix) or col_index >= len(game_matrix[0]):
                continue

            sum += game_matrix[row_index][col_index]

    return sum - game_matrix[row][col]


@nb.njit(parallel=True)
def get_next_generation(game_matrix, rows, cols):
    next_gen = init_matrix(False, rows, cols)

    for row in nb.prange(op.V_RES):
        for col in nb.prange(op.H_RES):
            if row >= len(game_matrix) or col >= len(game_matrix[0]):
                continue

            state = game_matrix[row][col]
            neighbors_number = count_cell_neighbors(game_matrix, row, col)

            if state == 0 and neighbors_number == 3:
                next_gen[row][col] = 1
            elif state == 1 and (neighbors_number < 2 or neighbors_number > 3):
                next_gen[row][col] = 0
            else:
                next_gen[row][col] = game_matrix[row][col]

    return next_gen


def set_game_matrix_cell_by_coords(x, y, game_matrix):
    if x < op.WIDTH and x >= 0 and y < op.HEIGHT and y >= 0:
        j, i = x // op.RESOLUTION, y // op.RESOLUTION
        game_matrix[i][j] = 1


@nb.jit(forceobj=True)
def main() -> None:
    pygame.init()

    pygame.display.set_caption("Game of life")
    screen = pygame.display.set_mode((op.WIDTH, op.HEIGHT))

    poligon_shape = PoligonShape(4)
    shape = PoligonShapeAdapter(screen, get_random_color(), poligon_shape)
    line_shape = LineShape(screen, get_random_color())

    game_matrix = init_matrix(True, op.V_RES, op.H_RES)

    running = True
    pause = False
    clock = pygame.time.Clock()
    lbm_pressed = False

    prev_x, prev_y = (0, 0)
    while running:
        events = pygame.event.get()
        for event in events:
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    pause = on_game_pause(event, pause)
                case pygame.MOUSEBUTTONDOWN:
                    lbm_pressed = True
                    if pygame.mouse.get_pressed()[0]:
                        x, y = pygame.mouse.get_pos()
                        prev_x, prev_y = x, y
                        set_game_matrix_cell_by_coords(x, y, game_matrix)

                    elif pygame.mouse.get_pressed()[2]:
                        pass
                case pygame.MOUSEBUTTONUP:
                    lbm_pressed = False
                case pygame.MOUSEMOTION:
                    if lbm_pressed:
                        x, y = pygame.mouse.get_pos()
                        
                        interploation = interpolate(x, y, prev_x, prev_y)

                        for prev_x_l, prev_y_l in interploation:
                            set_game_matrix_cell_by_coords(
                                int(prev_x_l), int(prev_y_l), game_matrix
                            )

                        prev_x, prev_y = x, y

        draw_matrix(game_matrix, shape, line_shape)
        pygame.display.update()
        screen.fill(BLACK)

        if not pause:
            clock.tick(op.MAX_FPS)
            game_matrix = get_next_generation(game_matrix, op.V_RES, op.H_RES)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        traceback.print_exception(ex)
