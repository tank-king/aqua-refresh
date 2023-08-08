from src.engine.objects import BaseObject
from src.engine.config import *
from src.engine.utils import *


class Splash(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y, WATER_SPLASH_LAYER)
        self.sheet = LoopingSpriteSheet(get_path('images', 'water', f'splash1.png'), 7, 3, 21, scale=0.75, timer=0.065)

    def update(self, events: list[pygame.event.Event], dt):
        if self.sheet.done:
            self.destroy()

    def draw(self, surf: pygame.Surface, offset):
        self.sheet.draw(surf, *self.pos)
