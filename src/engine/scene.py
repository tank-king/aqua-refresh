import importlib
import json
import random
import sys
import traceback
from pathlib import Path
from typing import Optional

import pygame

from src.engine.config import *
from src.engine.objects import *
from src.engine.save import WASMFetch
from src.engine.sounds import SoundManager
from src.engine.subtitles import SubtitleManager, BlinkingSubtitle, get_typed_subtitles, Subtitle
from src.engine.transition import TransitionManager
from src.engine.utils import *
from src.engine.physics import PhysicsManager


def update_error_handle(f):
    def wrapper(obj: 'Scene', events: list[pygame.event.Event], *args, **kwargs):
        try:
            f(obj, events, *args, **kwargs)
        except Exception as e:
            if not DEBUG:
                obj.raise_error(e)
            else:
                print('yo')
                raise e
            print(e)
            print(*traceback.format_exception(type(e), e, e.__traceback__))
        if obj.error:
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_e:
                        obj.show_traceback = True
                    if e.key == pygame.K_KP_PLUS:
                        obj.error_size += 2
                    if e.key == pygame.K_KP_MINUS:
                        obj.error_size -= 2
                    obj.error_size = clamp(obj.error_size, 5, 50)

    return wrapper


def draw_error_handle(f):
    def wrapper(obj: 'Scene', surf: pygame.Surface, *args, **kwargs):
        try:
            f(obj, surf, *args, **kwargs)
        except Exception as e:
            if DEBUG:
                raise e
            else:
                obj.raise_error(e)
            # print(e)
            # print(*traceback.format_exception(type(e), e, e.__traceback__))
        if obj.error:
            e = obj.error
            errors = traceback.format_exception(type(e), e, e.__traceback__)
            a = [i.split('\n') for i in errors]
            b = []
            for i in a:
                for x in i:
                    if x:
                        b.append(x)
            errors = b
            surf.fill(BG_COlOR)
            if obj.show_traceback:
                y = 150
                for i in errors:
                    t = text(i, obj.error_size)
                    y += obj.error_size
                    surf.blit(t, (50, y))
            else:
                t = text('Error', 150)
                surf.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                t = text('Press E to show traceback', 25)
                surf.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150)))

    return wrapper


class MetaClass(type):
    def __new__(mcs, name, bases, namespaces):
        for attr, attr_val in namespaces.items():
            if attr == 'update':
                namespaces[attr] = update_error_handle(attr_val)
            elif attr == 'draw':
                namespaces[attr] = draw_error_handle(attr_val)

        return super().__new__(mcs, name, bases, namespaces)


class Scene(BaseStructure, metaclass=MetaClass):
    """
    Base signature for all menus
    """

    def __init__(self, manager: 'SceneManager', name='menu'):
        self.manager = manager
        self.name = name
        self.error: Optional[Exception] = None
        self.show_traceback = False
        self.error_size = 25

    @staticmethod
    def get_menu_name():
        return 'none'

    def enter(self):
        pass

    def raise_error(self, exception: Exception):
        self.error = exception

    def reset(self):
        self.__init__(self.manager, self.name)

    def update(self, events: list[pygame.event.Event], dt):
        pass

    def exit(self):
        pass

    def draw(self, surf: pygame.Surface, offset):
        surf.blit(text(self.name), (50, 50))


class UnloadedScene(Scene):
    def draw(self, surf: pygame.Surface, offset):
        surf.fill(BG_COlOR)
        t = text('Unloaded Scene', 100)
        surf.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


class SceneManager(BaseStructure):
    def __init__(self):
        self.to_switch = 'none'  # to-switch transition
        self.to_reset = False
        self.to_save_in_stack = True
        self.transition_manager = TransitionManager()  # overall transition
        # self.objects_manager = ObjectManager()  # to be used across all menus
        self.subtitle_manager = SubtitleManager()  # overall subtitles
        # pre-set menus to be loaded initially
        self.fetch_api = WASMFetch()
        self.menu_references = {
        }
        self.menu_references.clear()
        this = sys.modules[__name__]
        self.menu_references = {i.__name__.lower(): i for i in [getattr(this, j) for j in dir(this)] if
                                isinstance(i, MetaClass) and type(i) != Scene}
        # path = Path(__file__).parent.parent / 'scenes'
        path = os.path.join(BASE_PATH, 'src', 'scenes')
        # path = os.path.join('src', 'scenes')
        scenes = [i for i in os.listdir(path.__str__()) if i.endswith('.py')]
        sys.path.append(path.__str__())
        for scene in scenes:
            scene_name = scene.removesuffix('.py')
            scene_name = f"src.scenes.{scene_name}"
            try:
                module = importlib.import_module(scene_name)
                for obj in [getattr(module, j) for j in dir(module)]:
                    if isinstance(obj, MetaClass):
                        self.menu_references[obj.__name__.lower()] = obj
            except ImportError as e:
                print(e)
                print(f"Could not import scene {scene_name}")
        self.menus: dict[str, Scene] = {}
        for i, _ in self.menu_references.items():
            self.menus[i] = self.menu_references.get(i)(self, i)
        print(self.menus)
        self.mode = 'home'
        self.menu = self.menus[self.mode]
        self.menu.enter()
        self.default_bg = pygame.Surface([WIDTH, HEIGHT])
        # self.bg = self.get_bg_for_menu(self.menu)
        self.mode_stack = []  # for stack based scene rendering
        self._default_reset = False
        self._default_transition = False
        self.camera_shake_intensity = 5

    def apply_camera_shake(self, intensity):
        self.camera_shake_intensity = intensity

    def get_bg_for_menu(self, menu):
        path = Path(__file__).parent.parent.parent / 'assets' / 'images' / menu / 'bg.png'
        if path.exists():
            return load_image(path)
        else:
            return self.default_bg

    def get_menu(self, menu):
        try:
            return self.menus[menu]
        except KeyError:
            return UnloadedScene(self, 'Error')

    def switch_to_prev_mode(self):
        try:
            self.switch_mode(self.mode_stack.pop(), self._default_reset, self._default_transition, save_in_stack=False)
        except IndexError:
            sys.exit(0)

    def switch_mode(self, mode, reset=False, transition=False, save_in_stack=False):
        if mode in self.menus:
            if transition:
                self.to_switch = mode
                self.to_reset = reset
                self.to_save_in_stack = save_in_stack
                self.transition_manager.close()
            else:
                if save_in_stack:
                    self.mode_stack.append(self.mode)
                self.mode = mode
                self.menu.exit()
                self.menu = self.menus[self.mode]
                self.menu.enter()
                if reset:
                    self.menu.reset()
                self.subtitle_manager.clear()

    def update(self, events: list[pygame.event.Event], dt):
        self.camera_shake_intensity *= 0.9 ** dt
        if self.to_switch != 'none':
            if self.transition_manager.transition.status == 'closed':
                self.switch_mode(self.to_switch, self.to_reset, transition=False, save_in_stack=self.to_save_in_stack)
                self.to_switch = 'none'
                self.to_reset = False
                self.transition_manager.open()
        self.menu.update(events, dt)
        self.transition_manager.update(events, dt)
        # self.objects_manager.update(events, dt)
        self.subtitle_manager.update(events, dt)
        # PhysicsManager.update(events, dt)
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    self.menu.reset()
                    self.menu.enter()
                if e.key == pygame.K_ESCAPE:
                    self.switch_to_prev_mode()
            if e.type == DISPLAY_SUBTITLE:
                try:
                    pos = e.pos
                except AttributeError:
                    pos = (WIDTH / 2, HEIGHT / 2)
                try:
                    t = e.time
                except AttributeError:
                    t = 2
                self.subtitle_manager.add_multiple(
                    get_typed_subtitles(e.text, pos=pos, _time=t),
                )
            # if e.key == pygame.K_s:
                #     self.camera_shake_intensity = 20

    def draw(self, surf: pygame.Surface, offset):
        if self.camera_shake_intensity > 0.1:
            k = round(self.camera_shake_intensity)
            offset = (random.randint(-k, k), random.randint(-k, k))
        self.menu.draw(surf, offset)
        self.transition_manager.draw(surf, offset)
        # self.objects_manager.draw(surf, offset)
        self.subtitle_manager.draw(surf, offset)

