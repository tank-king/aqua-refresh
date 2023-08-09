from src.engine.objects import BaseObject
from src.engine.utils import *


class ScoreText(BaseObject):
    def __init__(self, x, y, score: int, anchor='center'):
        super().__init__(x, y)
        self.score = score
        self.sign = '+' if score >= 0 else '-'
        self.alpha = 255
        self.text = text(f' {self.sign}{abs(self.score)}$ ', 45, bg_color='#511309')
        self.anchor = anchor

    def update(self, events: list[pygame.event.Event], dt):
        self.y -= dt * 2
        self.alpha -= dt * 5
        if self.alpha <= 0:
            self.alpha = 0
            self.destroy()
        self.text.set_alpha(self.alpha)

    def draw(self, surf: pygame.Surface, offset):
        rect = self.text.get_rect()
        rect.__setattr__(self.anchor, self.pos)
        surf.blit(self.text, rect)
