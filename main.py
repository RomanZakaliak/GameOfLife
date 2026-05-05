"""
=============================================================================
 main_gpu.py  –  Game of Life (GPU-accelerated entry point)
=============================================================================

This is the main loop for the GPU version of Conway's Game of Life.
It wires together three components:

  • pygame          – creates the window and delivers input events.
  • Renderer        – owns all OpenGL / ModernGL resources and runs the
                      Game-of-Life logic on the GPU via GLSL shaders.
  • InputHandler    – converts raw pygame events into high-level actions
                      (quit, pause, draw cells).

The loop itself is intentionally thin:

    1. Collect events  →  InputHandler
    2. React to flags  (quit / pause / draw cells)
    3. Step simulation (if not paused)
    4. Draw to screen
    5. Cap framerate
=============================================================================
"""

import pygame

from src import options as op
from src.input_handler import InputHandler
from src.renderer import Renderer


def main() -> None:
    # -----------------------------------------------------------------
    # 1. Initialise pygame
    # -----------------------------------------------------------------
    # pygame.OPENGL  – tells pygame to create an OpenGL-capable window
    #                  (required by ModernGL).
    # pygame.DOUBLEBUF – use double-buffering so we draw to an off-screen
    #                    buffer and flip it to the screen in one go,
    #                    preventing flicker.
    pygame.init()
    pygame.display.set_mode((op.WIDTH, op.HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Game of Life – GPU")

    renderer = Renderer()
    renderer.init_grid_random()

    input_handler = InputHandler(renderer.grid_width, renderer.grid_height)

    clock = pygame.time.Clock()
    paused = False

    running = True
    while running:
        input_handler.process_events(pygame.event.get())

        if input_handler.should_quit:
            running = False
            continue

        if input_handler.toggle_pause:
            paused = not paused

        if input_handler.cells_to_activate:
            renderer.write_cells(input_handler.cells_to_activate)

        if not paused:
            renderer.step()

        renderer.update_time_uniform(pygame.time.get_ticks() / 1000.0)
        renderer.draw()
        pygame.display.flip()

        # --- framerate cap --------------------------------------------
        clock.tick(op.TICK_RATE)

    renderer.release()
    pygame.quit()


if __name__ == "__main__":
    main()
