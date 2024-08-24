from abc import ABC, abstractmethod
from pygame import Surface, draw

from options import *

class CellShape(ABC):
    surface: Surface = None
    color: tuple = (255, 255, 255)

    def __init__(self, surface: Surface, color: tuple) -> None:
        super().__init__()

        self.surface = surface
        self.color = color

    @abstractmethod
    def draw(self, position, size) -> None:
        pass


class RectShape(CellShape):
    def __init__(self, surface: Surface, color: tuple) -> None:
        super().__init__(surface, color)
    
    def draw(self, position, size) -> None:
        x, y = position
        draw.rect(self.surface, self.color, [x - size//2, y - size//2, size, size])

class CircleShape(CellShape):
    def __init__(self, surface: Surface, color: tuple) -> None:
        super().__init__(surface, color)

    def draw(self, position, size) -> None:
        draw.circle(self.surface, self.color, position, size//2)
    
class LineShape(CellShape):
    def __init__(self, surface :Surface, color: tuple) -> None:
        super().__init__(surface, color)

    def draw(self, start_position, end_position) -> None:
        draw.line(self.surface, self.color, start_position, end_position, CELL_SIZE//4)