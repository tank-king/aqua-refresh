import pygame

from src.engine.objects import BaseObject
from src.engine.config import *


class PollutionMeter(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = 250
        self.thickness = 15

    def update(self, events: list[pygame.event.Event], dt):
        pass

    def draw(self, surf: pygame.Surface, offset):
        rect1 = pygame.Rect(0, 0, self.width, self.thickness)
        rect1.topleft = self.pos

        rect = pygame.Rect(0, 0, self.width * GAMESTATS.POLLUTION / 100, self.thickness)
        rect.topleft = self.pos
        pygame.draw.rect(surf, '#006994FF', rect1)
        pygame.draw.rect(surf, 'red', rect)

        pygame.draw.rect(surf, 'black', rect1, 4)


