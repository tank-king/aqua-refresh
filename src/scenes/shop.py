import random

import pygame

from src.engine.objects import ObjectManager
from src.engine.scene import Scene
from src.engine.ui import *
from src.objects.bubble import Bubble


class Powerup(BaseObject):
    def __init__(self, name, image, description, price, action=None):
        super().__init__(WIDTH / 2, HEIGHT / 2, UI_LAYER)
        self.name = name
        self.image = load_image(get_path('images', 'powerups', image), scale=0.6)
        self.w, self.h = 500, 600
        self.name_text = text(self.name, size=25)
        self.description = description
        self.description_text = text(self.description, size=25, wraplength=int(self.w * 3 / 4), color='#511309')
        self.price = price
        self.buy_button = Button(self.pos.x, self.pos.y + self.h / 2 - 50, f'Buy: {price} $', anchor='center',
                                 action=self.buy)
        self.action = action

    def use(self):
        if self.action:
            self.action()

    def buy(self):
        if GAMESTATS.MONEY >= self.price:
            GAMESTATS.MONEY -= self.price
            self.use()
        else:
            self.post_event(DISPLAY_SUBTITLE, text='Not Enough Money')

    def update(self, events: list[pygame.event.Event], dt):
        self.buy_button.update(events, dt)

    def draw(self, surf: pygame.Surface, offset):
        w, h = self.w, self.h
        rect = pygame.Rect(self.x - w / 2, self.y - h / 2, w, h)
        pygame.draw.rect(surf, '#DF9B26', rect)
        pygame.draw.rect(surf, 'black', rect, 3)
        surf.blit(self.name_text, self.name_text.get_rect(center=(self.pos.x, self.pos.y - 50)))
        surf.blit(self.image, self.image.get_rect(midtop=(self.x, self.y - h / 2 + 50)))
        surf.blit(self.description_text, self.description_text.get_rect(midtop=(self.x, self.pos.y)))
        self.buy_button.draw(surf, offset)


class Shop(Scene):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.object_manager = ObjectManager()
        self.object_manager.add_multiple(
            [
                Button(150, HEIGHT / 2, '<', anchor='center', text_size=100, action=self.decrement_index),
                Button(WIDTH - 150, HEIGHT / 2, '>', anchor='center', text_size=100, action=self.increment_index),
                Button(25, 25, 'Back', anchor='topleft', text_size=30,
                       action=lambda: self.manager.switch_mode('game', reset=False, transition=True)
                       ),
            ]
        )

        def purifier():
            for i in range(min(20, len(GAMESTATS.STAGNANT_GARBAGE))):
                GAMESTATS.STAGNANT_GARBAGE[i].destroy()
            GAMESTATS.decrease_pollution(10)

        self.powerups = [
            Powerup('Cleanser', 'powerup1.png', 'Decreases pollution by 10%', 50,
                    lambda: GAMESTATS.decrease_pollution(10)),
            Powerup('Hydrogen Peroxide', 'powerup2.png',
                    'Decreases pollution by 20%', 100,
                    lambda: GAMESTATS.decrease_pollution(20)),
            Powerup('Purifier', 'powerup3.png',
                    'cleans upto 20 garbage lying on bottom of water body and reduces pollution by 10%', 200,
                    purifier),
            # Powerup('Fountain', 'powerup4.png', 'improves oxygen supply and increases vegetation', 1500),
        ]

        self.index = 0

    def increment_index(self):
        self.index += 1
        self.index %= len(self.powerups)

    def decrement_index(self):
        self.index -= 1
        self.index %= len(self.powerups)

    @property
    def powerup(self):
        return self.powerups[self.index]

    def update(self, events: list[pygame.event.Event], dt):
        self.powerup.update(events, dt)
        self.object_manager.update(events, dt)
        self.object_manager.add(
            Bubble(random.randint(0, WIDTH), HEIGHT)
        )

    def draw(self, surf: pygame.Surface, offset):
        surf.fill("#006994")
        self.object_manager.draw(surf, offset)
        self.powerup.draw(surf, offset)
