import random

import pymunk

from src.engine.objects import BaseObject
from src.engine.utils import *
from src.objects.bubble import Bubble
from src.engine.config import *
from src.engine.physics import SpritePhysicsObject



class Fish(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y, FISH_LAYER)
        # self.sheet = LoopingSpriteSheet(get_path('images', 'fish', 'fish1.png'), 3, 4, scale=0.15, timer=0.08,
        #                                 smooth=True)
        index = random.choice([5, 7])
        self.sheet = LoopingSpriteSheet(get_path('images', 'fish', f'fish{index}.png'), 1, 1, scale=0.25, timer=0.08)
        self.bubble_timer = Timer(1)
        self.mode = 'a'

    def update(self, events: list[pygame.event.Event], dt):
        if self.bubble_timer.tick:
            self.bubble_timer.timeout = random.uniform(1, 3)
            for i in range(10):
                self.object_manager.add(
                    Bubble(*self.pos, radius=random.randint(1, 10), randomize_offset=False)
                )

    def draw(self, surf: pygame.Surface, offset):
        self.sheet.draw(surf, self.x, self.y)

#
# class Fish(SpritePhysicsObject):
#     def __init__(self, x, y):
#         index = random.choice([5, 7])
#         super().__init__(x, y, get_path('images', 'fish', f'fish{index}.png'), 1, 1, 1, mass=100, scale=0.25,
#                          body_type=pymunk.Body.KINEMATIC)
#         # self.sheet = LoopingSpriteSheet(get_path('images', 'fish', 'fish1.png'), 3, 4, scale=0.15, timer=0.08,
#         #                                 smooth=True)
#         # index = random.choice([5, 7])
#         # self.sheet = LoopingSpriteSheet(, 1, 1, scale=0.25, timer=0.08)
#
#     def update(self, events: list[pygame.event.Event], dt):
#         super().update(events, dt)
#         self.object_manager.add(
#             Bubble(*self.pos, radius=random.randint(1, 10))
#         )
#
#     def draw(self, surf: pygame.Surface, offset):
#         super().draw(surf, offset)
#         # self.sheet.draw(surf, self.x, self.y)
