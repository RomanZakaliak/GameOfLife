from __future__ import annotations

import math

import pygame

from src import options as op

LEFT_MOUSE_BUTTON = 1
MIDDLE_MOUSE_BUTTON = 2
RIGHT_MOUSE_BUTTON = 3


class InputHandler:
    def __init__(self, grid_width: int, grid_height: int) -> None:
        self._grid_w = grid_width
        self._grid_h = grid_height

        self.should_quit: bool = False
        self.toggle_pause: bool = False
        self.cells_to_activate: list[tuple[int, int]] = []

        self._lmb_held: bool = False
        self._prev_x: float = 0.0
        self._prev_y: float = 0.0


    def process_events(self, events: list[pygame.event.Event]) -> None:
        self.toggle_pause = False
        self.cells_to_activate = []

        for event in events:
            match event.type:
                case pygame.QUIT:
                    self.should_quit = True

                case pygame.KEYDOWN:
                    self._handle_key_down(event)

                case pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_down(event)

                case pygame.MOUSEBUTTONUP:
                    self._handle_mouse_up(event)

                case pygame.MOUSEMOTION:
                    self._handle_mouse_motion()

    def _handle_key_down(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_SPACE:
            self.toggle_pause = True

    def _handle_mouse_down(self, event: pygame.event.Event) -> None:
        if event.button != 1:  
            return

        self._lmb_held = True
        x, y = pygame.mouse.get_pos()
        self._prev_x, self._prev_y = float(x), float(y)

        cell = self._screen_to_grid(x, y)
        if cell is not None:
            self.cells_to_activate.append(cell)

    def _handle_mouse_up(self, event: pygame.event.Event) -> None:
        if event.button == LEFT_MOUSE_BUTTON:
            self._lmb_held = False

    def _handle_mouse_motion(self) -> None:
        if not self._lmb_held:
            return

        x, y = pygame.mouse.get_pos()
        interpolated = self._interpolate(float(x), float(y), self._prev_x, self._prev_y)
        self.cells_to_activate.extend(interpolated)
        self._prev_x, self._prev_y = float(x), float(y)

    def _screen_to_grid(self, sx: int, sy: int) -> tuple[int, int] | None:

        gx = int(sx / (op.WIDTH / self._grid_w))
        gy = self._grid_h - int(sy / (op.HEIGHT / self._grid_h)) - 1

        if 0 <= gx < self._grid_w and 0 <= gy < self._grid_h:
            return (gx, gy)
        return None

    def _interpolate(
        self, x: float, y: float, prev_x: float, prev_y: float
    ) -> list[tuple[int, int]]:
        dx = x - prev_x
        dy = y - prev_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 1.0:
            return []

        step = float(op.CELL_DELTA)
        cos_a = dx / distance
        sin_a = dy / distance

        cells: list[tuple[int, int]] = []
        walk_x, walk_y = prev_x, prev_y
        steps = int(distance / step)

        for _ in range(steps):
            cell = self._screen_to_grid(int(walk_x), int(walk_y))
            if cell is not None and cell not in cells:
                cells.append(cell)
            walk_x += cos_a * step
            walk_y += sin_a * step

        end_cell = self._screen_to_grid(int(x), int(y))
        if end_cell is not None and end_cell not in cells:
            cells.append(end_cell)

        return cells
