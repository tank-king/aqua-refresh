import math
import random
from operator import itemgetter
from typing import Type

import pygame

from src.engine.config import *
from src.engine.objects import BaseObject, Point
from src.engine.physics import SpritePhysicsObject, PhysicsObject, PhysicsManager
from src.engine.utils import get_path, Timer, LinearInterpolator
from src.objects.bubble import Bubble
from src.objects.score_text import ScoreText


# this = sys.modules[__name__]

class Garbage(SpritePhysicsObject):
    def get_sprite_sheet_args(self):
        raise NotImplementedError

    def get_mass(self):
        raise NotImplementedError

    def get_damping(self):
        raise NotImplementedError

    def get_scale(self):
        return 1

    def get_score(self):
        return 100

    def get_value(self):
        return 2

    def set_angle(self, angle):
        self.body.angle = angle

    def __init__(self, x, y):
        args = list(self.get_sprite_sheet_args())
        args[0] = get_path('images', 'garbage', args[0])
        super().__init__(x, y, *args, mass=self.get_mass(), scale=self.get_scale())
        self.damping = self.get_damping()
        self.body.velocity_func = self.custom_damping
        self.in_water = False
        self.set_angle(random.randint(0, 360))
        self.rest = False
        self.radius = Point().distance_to(self.sheet.image.get_size()) / 2
        self.radius = 90
        self.scale = LinearInterpolator(1, 0.1, 0)
        self.collected = False
        self.selected = False
        self.pollution_timer = Timer(1)
        # self.body.apply_impulse_at_local_point((0, 1000000))

    def custom_damping(self, body, gravity, damping, dt):
        self.body.update_velocity(body, gravity, self.damping, dt)

    def collect(self):
        self.post_event(ADD_ITEM_TO_TRASH, item=self)
        self.unregister_from_physics_space()
        self.collected = True
        self.rest = True

    def update(self, events: list[pygame.event.Event], dt):
        self.selected = False
        mx, my = pygame.mouse.get_pos()
        if self.pos.distance_to([mx, my]) <= self.radius:
            self.selected = True
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1 and not self.rest:
                    mx, my = pygame.mouse.get_pos()
                    if self.selected:
                        # self.object_manager.add(
                        #     ScoreText(*self.pos, self.get_score())
                        # )
                        self.collect()
                    else:
                        pass
                        # TODO
                        # self.object_manager.add(
                        #     ScoreText(mx, my, -20)
                        # )
        if not self.in_water:
            if max([i[1] + self.pos.y for i in self.shape.get_vertices()]) > WATER_DEPTH:
                self.in_water = True
                self.post_event(WATER_SPLASH, pos=self.pos, mass=self.get_mass())
        if self.pos.y > WATER_DEPTH:
            # curr_depth = self.pos.y - WATER_DEPTH
            # force = curr_depth * PhysicsManager.gravity().y * 0.05 * self.body.mass
            # self.body.apply_force_at_local_point((0, -force), (0, 0))
            self.damping = self.get_damping()
        else:
            self.damping = 1

        if self.collected:
            self.scale = self.scale.next
            self.object_manager.add(
                Bubble(*self.pos)
            )
            if self.scale.value <= 0.1:
                self.destroy()

        if not self.rest:
            linear_velocity_threshold = 0.1  # Adjust as needed
            angular_velocity_threshold = 0.5  # Adjust as needed

            is_almost_at_rest = (
                    abs(self.body.velocity.x) < linear_velocity_threshold and
                    abs(self.body.velocity.y) < linear_velocity_threshold and
                    abs(self.body.angular_velocity) < angular_velocity_threshold
            )
            if is_almost_at_rest:
                self.rest = True
                GAMESTATS.increase_pollution(1)
                GAMESTATS.STAGNANT_GARBAGE.append(self)
        if self.rest and not self.collected:
            if self.pollution_timer.tick:
                GAMESTATS.increase_pollution(0.05)

    def draw(self, surf: pygame.Surface, offset):
        self.sheet.draw(surf, *self.pos, math.degrees(-self.body.angle), size=self.scale.value)
        if self.selected and not self.rest:
            pygame.draw.polygon(surf, 'white', [
                (Point(i).rotate(math.degrees(self.body.angle)) + self.pos) for i in self.outline
            ], 5)
        # pygame.draw.circle(surf, 'red', self.pos, self.radius, 5)


class BottleGarbage(Garbage):
    def get_mass(self):
        return 5050

    def get_damping(self):
        return 0.98

    def get_scale(self):
        return 0.5

    def get_sprite_sheet_args(self):
        return 'bottle2.png', 1, 1, 1


class PlasticBag(Garbage):
    def get_mass(self):
        return 5050

    def get_damping(self):
        return 0.98

    def get_scale(self):
        return 0.5

    def get_sprite_sheet_args(self):
        return 'plastic-bag2.png', 1, 1, 1


class CanGarbage(Garbage):
    def get_mass(self):
        return 4000

    def get_damping(self):
        return 0.98

    def get_scale(self):
        return 0.25

    def get_sprite_sheet_args(self):
        index = random.choice([1, 2, 4])
        return f'can{index}.png', 1, 1, 1


class GarbageSpawner(BaseObject):
    def __init__(self, x=0, y=0, every=1):
        super().__init__(x, y)
        self.spawn_position = self.pos
        self.timer = Timer(timeout=every, reset=True)

    def spawn_garbage(self, garbage_possible: list[Type[Garbage]]):
        garbage: Garbage = random.choice(garbage_possible)(*self.spawn_position)
        self.object_manager.add(garbage)

    def change_spawn_location(self):
        offset = 100
        self.x = random.randint(offset, WIDTH - offset)
        self.spawn_position = self.pos

    def update(self, events: list[pygame.event.Event], dt):
        if self.timer.tick:
            # self.timer.timeout = 5
            self.spawn_garbage([BottleGarbage, CanGarbage])
            self.change_spawn_location()
