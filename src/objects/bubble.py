import random

import pygame

from src.engine.objects import BaseObject
from src.engine.utils import Timer, map_to_range
from src.engine.config import *

draw_circle = pygame.draw.circle


class Bubble(BaseObject):
    def __init__(self, x, y, radius=None, randomize_offset=True):
        if randomize_offset:
            x += random.randint(-20, 20)
        super().__init__(x, y, BUBBLE_LAYER)
        self.radius = radius if radius else random.randint(1, 20)
        self.outline_thickness = int(map_to_range(self.radius, 1, 20, 1, 5))

    def update(self, events: list[pygame.event.Event], dt):
        self.y -= dt * self.radius * 0.5
        self.x += random.randint(-1, 1) * dt
        self.radius -= dt * 0.2
        if self.radius <= 0 or self.y <= WATER_DEPTH:
            self.radius = 0
            self.post_event(BUBBLE_POP, x=self.x, y=self.y)
            self.destroy()

    def draw(self, surf: pygame.Surface, offset):
        draw_circle(surf, 'white', self.pos, self.radius, self.outline_thickness)
