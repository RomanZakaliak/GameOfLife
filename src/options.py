#Should be initialized before start execution
WIDTH = 1000 
HEIGHT = 700

# Could be changed duiring script execution using ui
TICK_RATE = 30
RESOLUTION = 10

# Depends on values above and does not change from ui
H_RES = WIDTH // RESOLUTION # Horizontal resolution
V_RES = HEIGHT // RESOLUTION # Vertical resolution

CELL_SIZE_RATE = 0.5 # Percent of resolution the cell should occupy (should be in range 0 to 1)
CELL_SIZE = int(RESOLUTION * CELL_SIZE_RATE)