import random

import pygame

from src.engine.objects import ObjectManager
from src.engine.scene import Scene
from src.engine.ui import *
from src.objects.bubble import Bubble


class Home(Scene):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.object_manager = ObjectManager()
        self.object_manager.add_multiple(
            [
                Button(WIDTH / 2, HEIGHT / 2, 'play', anchor='center', text_size=50,
                       action=lambda: self.manager.switch_mode('game', reset=True, transition=True)),
                Button(WIDTH / 2, HEIGHT / 2 + 100, 'Quit', anchor='center', text_size=50,
                       action=lambda: sys.exit(0)),
            ]
        )

    def update(self, events: list[pygame.event.Event], dt):
        self.object_manager.update(events, dt)
        self.object_manager.add(
            Bubble(random.randint(0, WIDTH), HEIGHT)
        )

    def draw(self, surf: pygame.Surface, offset):
        surf.fill("#006994")
        t = text('Aqua', 80, 'white')
        surf.blit(t, t.get_rect(center=(WIDTH / 2, 150)))
        t = text('Refresh', 80, 'white')
        surf.blit(t, t.get_rect(center=(WIDTH / 2, 250)))
        self.object_manager.draw(surf, offset)
