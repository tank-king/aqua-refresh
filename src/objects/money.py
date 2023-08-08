import pygame

from src.engine.objects import BaseObject
from src.engine.utils import *
from src.engine.config import *


class Money(BaseObject):
    def __init__(self):
        super().__init__(0, 0, UI_LAYER)
        self.value = GAMESTATS.MONEY
        self.to_add = 0
        self.add_rate = 1
        self.text = text(f'$ {self.value}', color='black')

    def add_money(self, money):
        self.to_add += money

    def update(self, events: list[pygame.event.Event], dt):
        self.text = text(f'$ {GAMESTATS.MONEY}', color='black')
        # if self.value != GAMESTATS.MONEY:
        #     _max = max(GAMESTATS.MONEY, self.value)
        #     self.value = _max
        #     GAMESTATS.MONEY = _max
        #     self.text = text(f'$ {self.value}', color='black')
        # if self.to_add > 0:
        #     rate = self.add_rate if self.to_add > self.add_rate else self.to_add
        #     self.to_add -= rate
        #     self.value += rate
        #     GAMESTATS.MONEY = +rate
        #     self.text = text(f'$ {self.value}', color='black')
        # else:
        #     self.value = GAMESTATS.MONEY
        #     self.to_add = 0
        for e in events:
            if e.type == ADD_MONEY:
                GAMESTATS.MONEY += e.money

    def draw(self, surf: pygame.Surface, offset):
        surf.blit(self.text, self.text.get_rect(center=(WIDTH / 2, self.text.get_height())))
