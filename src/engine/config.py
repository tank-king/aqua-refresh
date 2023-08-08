import os
import sys

# constants declaration
import pygame

GAME_NAME = 'aqua refresh'

WIDTH = 1000  # width of the screen
HEIGHT = 800  # height of the screen
SCREEN_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)
SCREEN_COLLISION_RECT = SCREEN_RECT.inflate(100, 100)

VIEWPORT_OFFSET = [0, 0, 0, 0]  # left right top bottom
VIEWPORT_RECT = pygame.Rect(
    VIEWPORT_OFFSET[0],
    VIEWPORT_OFFSET[2],
    WIDTH - VIEWPORT_OFFSET[0] - VIEWPORT_OFFSET[1],
    HEIGHT - VIEWPORT_OFFSET[2] - VIEWPORT_OFFSET[3]
)
BG_COlOR = (247, 213, 147)
TEXT_COLOR = '#511309'
VOLUME = 100  # sound volume
FPS = 60
TARGET_FPS = 60
ASSETS = 'assets'
WATER_DEPTH = 150

(
    SONG_FINISHED_EVENT,
    BUBBLE_POP,
    WATER_SPLASH,
    ADD_ITEM_TO_TRASH,
    DISPLAY_SUBTITLE,
    ADD_MONEY,
    *_,
) = (pygame.event.custom_type() for _ in range(10))

(
    WATER_SPLASH_LAYER,
    WATER_LAYER,
    OBJECTS_LAYER,
    FISH_LAYER,
    BUBBLE_LAYER,
    UI_LAYER,
    *_
) = range(0, 10)

SCORE_ADD_RATE = 5


class GAMESTATS:
    MONEY = 0
    POLLUTION = 75
    STAGNANT_GARBAGE = []

    @classmethod
    def increase_pollution(cls, quantity):
        cls.POLLUTION += quantity
        cls.POLLUTION = pygame.math.clamp(cls.POLLUTION, 0, 100)

    @classmethod
    def decrease_pollution(cls, quantity):
        cls.POLLUTION -= quantity
        cls.POLLUTION = pygame.math.clamp(cls.POLLUTION, 0, 100)

    @classmethod
    def reset(cls):
        cls.MONEY = 0
        cls.POLLUTION = 75
        for i in cls.STAGNANT_GARBAGE:
            i.destroy()
        cls.STAGNANT_GARBAGE.clear()
        cls.STAGNANT_GARBAGE = []


DEBUG = True

NUMPY = True
SCIPY = True

try:
    import numpy
except ImportError:
    numpy = ...
    NUMPY = False

try:
    import scipy
except ImportError:
    scipy = ...
    SCIPY = False


# for handling global objects

class Globals:
    _global_dict = {}

    @classmethod
    def set_global(cls, key, value):
        cls._global_dict[key] = value

    @classmethod
    def get_global(cls, key):
        return cls._global_dict.get(key)

    @classmethod
    def pop_global(cls, key):
        try:
            cls._global_dict.pop(key)
        except KeyError:
            pass


# for closing pyinstaller splash screen if loaded from bundle

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print('running in a PyInstaller bundle')
    ASSETS = os.path.join(sys._MEIPASS, ASSETS)
    try:
        import pyi_splash

        pyi_splash.close()
    except ImportError:
        pass
else:
    print('running in a normal Python process')
