WIDTH = 1200
HEIGHT = 800

TICK_RATE = 25


RESOLUTION = 10

H_RES = WIDTH // RESOLUTION + 1
V_RES = HEIGHT // RESOLUTION + 1

CELL_SIZE_RATE = 1.0

# The distance in pixels between two adjacent cells when drawing with the mouse.
CELL_DELTA = int(RESOLUTION * CELL_SIZE_RATE)
