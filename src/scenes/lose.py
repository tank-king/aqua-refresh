import random

import pygame

from src.engine.objects import ObjectManager
from src.engine.scene import Scene
from src.engine.ui import *
from src.objects.bubble import Bubble


class Lose(Scene):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.object_manager = ObjectManager()
        self.object_manager.add_multiple(
            [
                Button(WIDTH / 2, HEIGHT / 2, 'Replay', anchor='center', text_size=50,
                       action=lambda: self.manager.switch_mode('game', reset=True, transition=True)),
                Button(WIDTH / 2, HEIGHT / 2 + 100, 'Quit', anchor='center', text_size=50,
                       action=lambda: sys.exit(0)),
            ]
        )

    def enter(self):
        BaseObject().post_event(DISPLAY_SUBTITLE, text='Better luck next time!', pos=(WIDTH / 2, 100), time='inf')

    def update(self, events: list[pygame.event.Event], dt):
        self.object_manager.update(events, dt)
        self.object_manager.add(
            Bubble(random.randint(0, WIDTH), HEIGHT)
        )

    def draw(self, surf: pygame.Surface, offset):
        surf.fill("#006994")
        t = text('You Lost!', 60, 'white')
        surf.blit(t, t.get_rect(center=(WIDTH / 2, 200)))
        self.object_manager.draw(surf, offset)
