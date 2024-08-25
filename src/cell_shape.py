from abc import ABC, abstractmethod
from pygame import Surface, draw
import math

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


class PoligonShape():
    def __init__(self, vertices_number) -> None:
        self.vertices_number = vertices_number

    def draw(self, surface, color, position, size):
        x, y = position
        points = []

        for angle in range(0, 360, 360//self.vertices_number):
            angle_radians = angle * math.pi / 180
            p = (x + (size // 2) * math.cos(angle_radians), y + (size // 2) * math.sin(angle_radians))
            points.append(p)
        
        draw.polygon(surface, color, points)

class PoligonShapeAdapter(CellShape):
    def __init__(self, surface: Surface, color: tuple, poligon_shape: PoligonShape) -> None:
        super().__init__(surface, color)
        self.poligon_shape = poligon_shape

    def draw(self, position, size) -> None:
        self.poligon_shape.draw(self.surface, self.color, position, size)


        