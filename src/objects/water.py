import random

import pygame

from src.engine.objects import BaseObject, Point
from src.engine.config import *
from src.objects.splash import Splash


class WaterSpring(BaseObject):
    def __init__(self, x, y, height, target_height=None):
        super().__init__(x, y)
        if not target_height:
            self.target_height = height - 10
        else:
            self.target_height = target_height
        self.dampening = 0.05  # adjust accordingly
        self.tension = 0.01
        self.height = self.target_height
        self.vel = 0
        self.x = x
        self.y = y

    def update(self, events: list[pygame.event.Event], dt):
        dh = self.target_height - self.height
        if abs(dh) < 0.01:
            self.height = self.target_height
        self.vel += (self.tension * dh - self.vel * self.dampening) * dt
        self.height += self.vel * dt

    def draw(self, surf: pygame.Surface, offset):
        pygame.draw.circle(surf, 'white', [self.x, self.y + self.height], 1)


class Water(BaseObject):
    def __init__(self, x, y, width, height, depth=0, transparency=False):
        super().__init__(x, y, WATER_LAYER)
        diff = round(20 * 1.5)
        self.springs = [WaterSpring(x=i * diff, y=0, height=depth) for i in range(width // diff + 2)]
        self.diff = diff
        self.width = width
        self.height = height
        self.depth = depth
        self.points = [Point(i.x, i.height) for i in self.springs]
        self.points.extend([Point(self.width, self.height), Point(0, self.height)])
        # self.splash(len(self.springs) // 2, 40)
        self.surf = pygame.Surface([width, height], pygame.SRCALPHA)
        self.transparency = transparency

    @property
    def water_color(self):
        return pygame.Color('#006994FF').lerp(pygame.Color('black'), GAMESTATS.POLLUTION / 150)

    def get_points(self, offset=(0, 0)):
        self.points = [Point(offset[0] + i.x, offset[1] + i.height) for i in self.springs]
        if SCIPY and True:
            self.points = get_curve(self.points)
        self.points.extend(
            [
                Point(offset[0] + self.width, offset[1] + self.height),
                Point(offset[0], offset[1] + self.height)
            ]
        )

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_spring_index_for_x_pos(self, x):
        return int((x - self.x) // self.diff)

    def get_target_height(self):
        return self.springs[0].target_height

    def set_target_height(self, height):
        for i in self.springs:
            i.target_height = height

    def add_volume(self, volume):
        height = volume / self.height
        self.set_target_height(self.get_target_height() - height)

    def update(self, events: list[pygame.event.Event], dt):
        for i in self.springs:
            i.update(events, dt)
        self.spread_wave(dt)
        self.get_points(offset=self.pos)
        for e in events:
            if e.type == BUBBLE_POP:
                if e.y <= self.y + self.depth + 10:
                    self.splash(self.get_spring_index_for_x_pos(e.x), -2)
            if e.type == WATER_SPLASH:
                self.splash(self.get_spring_index_for_x_pos(e.pos.x), e.mass * 0.0065)
                self.object_manager.add(
                    Splash(e.pos.x, e.pos.y + 45)
                )
        index = random.randint(0, len(self.springs) - 1)
        self.splash(index, 0.5 * dt)
        # self.points.extend([Point(self.springs[-1].x, self.y + self.height), Point(self.x, self.y + self.height)])

    def draw(self, surf: pygame.Surface, offset):
        # self.surf.fill(0)
        pygame.draw.polygon(surf, pygame.Color(self.water_color), self.points)
        # surf.blit(self.surf, self.pos)

    def draw_line(self, surf: pygame.Surface):
        pygame.draw.lines(surf, 'white', False, self.points[:-2], 5)

    def spread_wave(self, dt=1.0):
        spread = 0.08 * dt
        for i in range(len(self.springs)):
            if i > 0:
                self.springs[i - 1].vel += spread * (self.springs[i].height - self.springs[i - 1].height)
            try:
                self.springs[i + 1].vel += spread * (self.springs[i].height - self.springs[i + 1].height)
            except IndexError:
                pass

    def splash(self, index, vel):
        try:
            self.springs[index].vel += vel
        except IndexError:
            pass


def get_curve(points):
    x_new = numpy.arange(points[0].x, points[-1].x, 1)
    x = numpy.array([i.x for i in points[:-1]])
    y = numpy.array([i.y for i in points[:-1]])
    f = scipy.interpolate.interp1d(x, y, kind='cubic', fill_value='extrapolate')
    y_new = f(x_new)
    x1 = x_new
    y1 = y_new
    # x1 = list(x_new)
    # y1 = list(y_new)
    points = [Point(x1[i], y1[i]) for i in range(len(x1))]
    return points
