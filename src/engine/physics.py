import math
from typing import Union

import pygame

from src.engine.config import TARGET_FPS, WIDTH, HEIGHT
from src.engine.objects import BaseObject, BaseStructure, Point
import pymunk

from src.engine.utils import Timer, LoopingSpriteSheet
from operator import attrgetter, itemgetter

_space = pymunk.Space()
_space.gravity = (0, 500)


# exit()

class PhysicsObject(BaseObject):
    def __init__(self, x, y, points, mass=150, body_type=pymunk.Body.DYNAMIC, draw=True, timer='inf', color='white'):
        super().__init__(x, y)
        self._draw = draw
        moment = pymunk.moment_for_poly(mass, points, (0, 0))
        self.body = pymunk.Body(mass=mass, moment=moment, body_type=body_type)
        self.body.position = (x, y)
        self.shape = pymunk.Poly(self.body, points)

        left, right = min(points, key=itemgetter(0)), max(points, key=itemgetter(0))
        top, bottom = min(points, key=itemgetter(1)), max(points, key=itemgetter(1))
        self.width = right[0] - left[0]
        self.height = bottom[1] - top[1]

        _space.add(self.body, self.shape)
        self.timer = Timer(timer)
        self.color = color

    @staticmethod
    def create_wall(x, y, size):
        points = [(-size[0] // 2, -size[1] // 2), (-size[0] // 2, size[1] // 2), (size[0] // 2, size[1] // 2),
                  (size[0] // 2, -size[1] // 2)]
        obj = PhysicsObject(x, y, points, mass=10000, body_type=pymunk.Body.STATIC, draw=False)
        obj.shape.friction = 0.25
        return obj

    @property
    def pos(self):
        return pygame.Vector2(*self.body.position)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.body.position.x - self.width // 2, self.body.position.y - self.height // 2, self.width,
                           self.height)

    def destroy(self):
        super().destroy()
        self.unregister_from_physics_space()

    def unregister_from_physics_space(self):
        try:
            _space.remove(self.body, self.shape)
        except AssertionError:
            pass

    def update(self, events: list[pygame.event.Event], dt):
        if self.timer.tick:
            self.destroy()

    def draw(self, surf: pygame.Surface, offset):
        if not self._draw:
            return
        angle = self.shape.body.angle
        angle = math.degrees(angle)
        vertices = self.shape.get_vertices()
        vertices = [pygame.Vector2(i[0], i[1]) for i in vertices]
        vertices = [(i.rotate(angle) + self.pos + offset) for i in vertices]
        pygame.draw.polygon(surf, self.color, vertices)


class SpritePhysicsObject(PhysicsObject):
    def __init__(self, x, y, sprite_sheet, rows, cols, images, mass, scale=1, timer='inf', flipped=(0, 0),
                 body_type=pymunk.Body.DYNAMIC):
        self.sheet = LoopingSpriteSheet(sprite_sheet, rows, cols, images, scale=scale, flipped=flipped)
        w, h = self.sheet.size
        self.mask = pygame.mask.from_surface(self.sheet.image, 50)
        points = [(i[0] - w / 2, i[1] - h / 2) for i in self.mask.outline(10)]
        self.outline = points
        super().__init__(x, y, points, mass, timer=timer, body_type=body_type)
        self._draw = False
        self.shape.friction = 0.5

    def draw(self, surf: pygame.Surface, offset):
        super().draw(surf, offset)
        self.sheet.draw(surf, *self.pos, math.degrees(-self.body.angle))
        # pygame.draw.polygon(
        #     surf, 'red', [[i[0] + self.pos.x, i[1] + self.pos.y] for i in self.shape.get_vertices()], 5
        # )


class PhysicsManager(BaseStructure):
    # _added = False
    # _object_manager =
    @classmethod
    def gravity(cls):
        return _space.gravity

    @classmethod
    def clear(cls):
        # objects: list[Union[pymunk.Shape, pymunk.Body, pymunk.Constraint]] = _space.shapes
        # objects.extend(_space.bodies)
        # objects.extend(_space.constraints)
        # for i in objects:
        #     _space.remove(i)
        _space.remove(*_space.bodies, *_space.shapes)

    @classmethod
    def update(cls, events: list[pygame.event.Event], dt):
        # if not cls._added:
        #     cls._added = True
        #     _space.add(
        #
        #     )
        _space.step(dt / TARGET_FPS)
