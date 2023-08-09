import random

import pymunk

from src.engine.objects import ObjectManager, AnimatedSpriteObject
from src.engine.scene import Scene
from src.engine.config import *
from src.engine.ui import Button
from src.engine.utils import get_path, LoopingSpriteSheet
from src.objects.bubble import Bubble
from src.objects.fish import Fish
from src.objects.garbage import GarbageSpawner, BottleGarbage, CanGarbage
from src.objects.garbage_bin import GarbageBin
from src.objects.money import Money
from src.objects.pollution_meter import PollutionMeter
from src.objects.water import Water
from src.engine.physics import PhysicsObject, SpritePhysicsObject, PhysicsManager


class Game(Scene):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.object_manager = ObjectManager()
        PhysicsManager.clear()
        wall_scale = 0.8
        self.object_manager.add_multiple(
            [
                water := Water(0, 0, WIDTH, HEIGHT, depth=WATER_DEPTH),
                # Fish(250, 450),
                # Fish(500, 400),
                GarbageSpawner(WIDTH / 2, - 100),
                PhysicsObject.create_wall(WIDTH / 2, HEIGHT + 50, (WIDTH, 100)),
                # PhysicsObject.create_wall(-50, HEIGHT / 2, (100, HEIGHT)),
                # PhysicsObject.create_wall(WIDTH + 50, HEIGHT / 2, (100, HEIGHT)),
                SpritePhysicsObject(50 * wall_scale, HEIGHT / 2 + 40,
                                    get_path('images', 'wall', 'left-wall.png'),
                                    1, 1, 1,
                                    body_type=pymunk.Body.STATIC, mass=10000, scale=wall_scale),
                SpritePhysicsObject(WIDTH - 50 * wall_scale, HEIGHT / 2 + 40,
                                    get_path('images', 'wall', 'right-wall.png'),
                                    1, 1, 1,
                                    body_type=pymunk.Body.STATIC, mass=10000, scale=wall_scale),
                AnimatedSpriteObject(WIDTH / 2, HEIGHT, WATER_LAYER,
                                     get_path('images', 'wall', 'base-center.png'),
                                     1, 1, 1, scale=wall_scale
                                     ),
                GarbageBin(WIDTH - 100, 75),
                Money(),
                Button(x=25, y=50, label=' Shop ',
                       action=lambda: self.manager.switch_mode('shop', transition=True)),
                PollutionMeter(15, 15)
            ]
        )
        self.water = water
        self.surf = None
        GAMESTATS.reset()
        # self.scale = wall_scale
        # self.left = LoopingSpriteSheet(get_path('images', 'wall', 'left-wall.png'), 1, 1, 1, scale=wall_scale)
        # self.right = LoopingSpriteSheet(get_path('images', 'wall', 'right-wall.png'), 1, 1, 1, scale=wall_scale)

    def get_level_config(self, level):
        config = {
            # level: [toxicity, timer,
        }
        return config

    def update(self, events: list[pygame.event.Event], dt):
        super().update(events, dt)
        self.object_manager.update(events, dt)
        if GAMESTATS.POLLUTION >= 100:
            self.manager.switch_mode('lose', reset=True, transition=True)
        if GAMESTATS.POLLUTION <= 0 and len(GAMESTATS.STAGNANT_GARBAGE) == 0:
            self.manager.switch_mode('win', reset=True, transition=True)
        # if pygame.mouse.get_pressed(3)[0]:
        #     mx, my = pygame.mouse.get_pos()
        #     self.object_manager.add(Bubble(mx, my))
        PhysicsManager.update(events, dt)

    def draw(self, surf: pygame.Surface, offset):
        # if not self.surf:
        #     self.surf = pygame.Surface([*surf.get_size()], pygame.SRCALPHA)
        bg = 'white'
        surf.fill(bg)
        self.object_manager.draw(surf, offset)
        # self.left.draw(surf, 120 * self.scale, HEIGHT / 2 + 40)
        # self.right.draw(surf, WIDTH - 106 * self.scale, HEIGHT / 2 + 40)
