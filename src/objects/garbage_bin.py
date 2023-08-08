import pygame.mouse

from src.engine.objects import BaseObject
from src.engine.config import *
from src.engine.utils import *


class GarbageBin(BaseObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.level = 3
        self.sheet = LoopingSpriteSheet(get_path('images', 'trash-can', f'bin{self.level}.png'), 1, 1, 1, scale=0.5)
        self.items = []
        self.worth = 0
        self.item_limits = {
            1: 5,
            2: 10,
            3: 10
        }
        self.item_limit = self.item_limits[self.level]
        self.label_text = self.label_text = f"{len(self.items)}/{self.item_limit}"
        self.text_size = 25
        self.text = self.get_text()
        self.selected = False
        self.outline = pygame.mask.from_surface(self.sheet.image).outline()
        self.timer = Timer(1)
        self.label_visible = True

    @property
    def rect(self) -> pygame.Rect:
        return self.sheet.image.get_rect()

    def update(self, events: list[pygame.event.Event], dt):
        button_pressed = False
        for e in events:
            if e.type == ADD_ITEM_TO_TRASH:
                self.add_item(item_name='garbage', worth=e.item.get_value())
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    button_pressed = True
        if self.sheet.image.get_rect(center=self.pos).collidepoint(pygame.mouse.get_pos()):
            if button_pressed:
                self.sell_items()
            self.selected = True
            self.show_label()
        else:
            self.selected = False
        if self.timer.tick:
            self.label_visible = False
        if self.full:
            self.show_label()

    def show_label(self):
        self.timer.reset()
        self.label_visible = True

    def add_item(self, item_name, worth):
        if len(self.items) >= self.item_limit:
            return
        self.show_label()
        self.items.append(item_name)
        self.worth += worth
        self.text = self.get_text()

    def get_text(self):
        self.label_text = f" {len(self.items)}/{self.item_limit} "
        return text(self.label_text, size=self.text_size, bg_color='#511309')

    def sell_items(self):
        self.post_event(ADD_MONEY, money=self.worth)
        self.worth = 0
        self.items = []
        self.text = self.get_text()

    @property
    def full(self):
        return len(self.items) >= self.item_limit

    def draw(self, surf: pygame.Surface, offset):
        self.sheet.draw(surf, *self.pos)
        if self.selected:
            points = [[i[0] + self.pos.x - self.rect.w / 2, i[1] + self.pos.y - self.rect.h / 2] for i in self.outline]
            pygame.draw.polygon(surf, 'black', points, 5)
        if self.label_visible:
            if not self.full:
                surf.blit(self.text, self.text.get_rect(midtop=self.pos))
            else:
                surf.blit(t := text(' Sell ', size=self.text_size, bg_color='#511309'), t.get_rect(midtop=self.pos))
