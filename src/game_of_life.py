import pygame
import random
import numpy as np
import numba as nb
import math

import traceback

import options as op
from event_handlers import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def get_random_color():
    return (100, 100, 100)
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

@nb.njit
def init_matrix(fill_random :bool, rows, cols):
    if fill_random:
        return np.random.randint(0, 2, size=(rows, cols))
        
    return np.zeros((rows, cols), dtype=nb.int64)

@nb.jit(forceobj=True, looplift=False, parallel=True)
def draw_matrix(game_matrix, screen: pygame.Surface) -> None:
    for row in nb.prange(op.V_RES):
        for col in nb.prange(op.H_RES):
            if row >= len(game_matrix) or col >= len(game_matrix[0]):
                continue

            if game_matrix[row][col] == 1:
                pygame.draw.rect(screen, 
                    ((row * col) % 255, 
                    (col * op.V_RES) % 255, 
                    (row * op.H_RES) % 255), 
                    [col * op.RESOLUTION - op.CELL_SIZE//2, 
                     row * op.RESOLUTION - op.CELL_SIZE//2, 
                     op.CELL_SIZE, 
                     op.CELL_SIZE])

                # pygame.draw.circle(screen, 
                #     (100, 150, 100),
                #     [col * op.RESOLUTION, 
                #     row * op.RESOLUTION],
                #     op.CELL_SIZE//2)
                
                for i in nb.prange(-1, 2):
                    for j in nb.prange(-1, 2):
                        row_index = (row + i)
                        col_index = (col + j)

                        if row_index >= len(game_matrix) or \
                            col_index >= len(game_matrix[0]) or \
                            game_matrix[row_index][col_index] == 0:
                            continue

                        pygame.draw.line(screen, 
                             get_random_color(), 
                             [col * op.RESOLUTION, row * op.RESOLUTION], 
                             [col_index * op.RESOLUTION, row_index * op.RESOLUTION], op.RESOLUTION//5)

@nb.jit(fastmath=True, parallel=True)
def count_cell_neighbors(game_matrix, row :int, col:int) -> int:
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
        print(i, j)
        game_matrix[i][j] = 1 

@nb.njit(fastmath=True)
def get_euclidean_distance(x1, y1, x2, y2):
    return int(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))

@nb.jit(forceobj=True)
def main() -> None:
    pygame.init()
    

    pygame.display.set_caption("Game of life")
    screen = pygame.display.set_mode((op.WIDTH, op.HEIGHT))

    game_matrix = init_matrix(False, op.V_RES, op.H_RES)

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

                        angle = math.pi + math.atan2(prev_y - y, prev_x - x)
                        angle_sin = math.sin(angle)
                        angle_cos = math.cos(angle)

                        distance = get_euclidean_distance(x, y, prev_x, prev_y)
                        prev_x_l, prev_y_l = prev_x, prev_y
                        for _ in range(0, distance // op.CELL_SIZE):
                            set_game_matrix_cell_by_coords(int(prev_x_l), int(prev_y_l), game_matrix)
                            prev_x_l, prev_y_l = prev_x_l + angle_cos * op.CELL_SIZE, prev_y_l + angle_sin * op.CELL_SIZE

                        prev_x, prev_y = x, y

        # op.H_RES = op.WIDTH // op.RESOLUTION # Horizontal resolution
        # op.V_RES = op.HEIGHT // op.RESOLUTION # Vertical resolution

        draw_matrix(game_matrix, screen)
        pygame.display.update()
        screen.fill(BLACK)

        if not pause:
            clock.tick(op.TICK_RATE)
            game_matrix = get_next_generation(game_matrix, op.V_RES, op.H_RES)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        traceback.print_exception(ex)