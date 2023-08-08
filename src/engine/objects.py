import random
from operator import attrgetter
from typing import Union, Sequence

import pygame.event

from src.engine.config import *
# from src.engine.physics import PhysicsManager, RectPhysicsObject
from src.engine.utils import *

draw_circle = pygame.draw.circle
Point = pygame.Vector2


class BaseStructure:
    def update(self, events: list[pygame.event.Event], dt):
        pass

    def draw(self, surf: pygame.Surface, offset):
        pass


class BaseObject(BaseStructure):
    def __init__(self, x=0.0, y=0.0, z=OBJECTS_LAYER):
        self.x, self.y = x, y
        self.alive = True
        self.z = z  # for sorting
        self.object_manager: Union[ObjectManager, None] = None

    def destroy(self):
        self.alive = False

    @staticmethod
    def post_event(event, **kwargs):
        pygame.event.post(pygame.event.Event(event, kwargs))

    @property
    def pos(self):
        return Point(self.x, self.y)

    @pos.setter
    def pos(self, value):
        self.x, self.y = value

    @pos.setter
    def pos(self, position):
        self.x, self.y = position

    @property
    def rect(self) -> pygame.Rect:
        raise NotImplementedError

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_to(self, x, y):
        dx, dy = x - self.x, y - self.y
        self.move(dx, dy)

    def adjust_pos(self, ignore_x=False, ignore_y=False):
        if ignore_x:
            x = self.x
        else:
            x = clamp(self.x, VIEWPORT_RECT.left + self.rect.w // 2, VIEWPORT_RECT.right - self.rect.w // 2)
        if ignore_y:
            y = self.y
        else:
            y = clamp(self.y, VIEWPORT_RECT.top + self.rect.h // 2, VIEWPORT_RECT.bottom - self.rect.h // 2)
        self.move_to(x, y)

    def draw_glow(self, surf: pygame.Surface, offset):
        pass


class AnimatedSpriteObject(BaseObject):
    def __init__(self, x, y, z, sheet, rows, cols, images=None, alpha=True, scale=1.0, flipped=(0, 0),
                 color_key=None, timer=0.1, mode: Literal['center', 'topleft'] = 'center', smooth=True):
        self.sheet = LoopingSpriteSheet(
            sheet, rows, cols, images,
            alpha, scale, flipped, color_key, timer, mode, smooth
        )
        self.angle = 0
        self.scale = 1
        super().__init__(x, y, z)

    def draw(self, surf: pygame.Surface, offset):
        self.sheet.draw(surf, *self.pos, self.angle, self.scale)


class Component(BaseObject):
    def __init__(
            self,
            x, y,
            looping_sprite_sheet: LoopingSpriteSheet,
            appear=False, appear_vec=(0, 0), timer=0.1, speed=5,
            mask_offset=0, mask_speed=5.0, mask_length=10,
            blink_sequence=(),
            label='component'
    ):
        self.looping_sprite_sheet = looping_sprite_sheet
        self.appear = appear
        self.appear_sprite = AppearSprite(self.looping_sprite_sheet.images[0], appear_vec, timer, speed)
        super(Component, self).__init__(x, y)
        self.image = self.looping_sprite_sheet.image
        self.masks = pygame.mask.from_surface(self.image)
        self.outline = self.masks.outline(1)
        self._c = 0
        self.c = 0
        self._started = False
        self._draw_outline = False
        self._outline_done = False
        self.masking_offset = mask_offset
        self.max_mask_length = len(self.outline) // 4
        self.max_mask_length = mask_length
        self.mask_speed = mask_speed
        self.mask_color = 'white'
        self.outline_animation_callback = None
        self.blink_timer = Timer('inf', reset=True)
        # self.blink_timer.set_callback(self.toggle_visibility)
        self.blink_sequence: list = list(blink_sequence)
        self.visible = True
        self.surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.label = label
        self.size_scale = 1
        self.scale_reduction_rate = 0.95
        # if 'base' in label:
        #     self.boost_size()

    def boost_size(self, scale=1.5, reduction_rate=0.95):
        self.size_scale = scale
        self.scale_reduction_rate = reduction_rate

    def skip_to_start(self):
        self.start()
        self.blink_sequence = []
        self._draw_outline = False
        self.visible = True
        self.appear_sprite.skip()

    def start(self):
        self._started = True
        if self.blink_sequence:
            self.add_blink_sequence(*self.blink_sequence, clear=True)

    @staticmethod
    def get_blink_sequence(interval, count):
        return [interval] * count * 2

    @property
    def width(self):
        return self.looping_sprite_sheet.images[0].get_width()

    @property
    def height(self):
        return self.looping_sprite_sheet.images[0].get_height()

    @property
    def size(self):
        return self.width, self.height

    @property
    def outline_done(self):
        return self._outline_done

    @property
    def outline_animation_running(self):
        return self._draw_outline

    @property
    def rect(self) -> pygame.Rect:
        return self.looping_sprite_sheet.image.get_rect(center=(self.x, self.y))

    @staticmethod
    def bezier_blend(t):
        return t * t * (3.0 - 2.0 * t)

    def toggle_visibility(self):
        self.visible = not self.visible

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def add_blink_sequence(self, *args, clear=False):
        if clear:
            self.blink_sequence = list(args)[1:]
            self.blink_timer = Timer(args[0])
        else:
            self.blink_sequence.extend(args)

    def do_outline_animation(self, mask_speed=None, mask_offset=None, mask_length=None, mask_color=None, callback=None):
        self._draw_outline = True
        self._outline_done = False
        self._c = 0
        self.c = 0
        if mask_speed:
            self.mask_speed = mask_speed
        if mask_offset:
            self.masking_offset = mask_offset
        if mask_length:
            self.max_mask_length = mask_length
        if mask_color:
            self.mask_color = mask_color
        if callback:
            self.outline_animation_callback = callback

    def stop_outline_animation(self):
        self._draw_outline = False
        self._outline_done = False
        self._c = 0
        self.c = 0

    def update(self, events: list[pygame.event.Event], dt):
        if self._started:
            if self.appear and not self.appear_sprite.done:
                self.appear_sprite.update(events, dt)
            else:
                pass
        self.size_scale *= self.scale_reduction_rate ** dt
        self.size_scale = clamp(self.size_scale, 1, 2)
        if self._draw_outline:
            self._c += self.mask_speed
            self.c = int(self._c)
            mid = len(self.outline) // 2
            if self.c > mid * 2:
                self._draw_outline = False
                if self.outline_animation_callback:
                    self.outline_animation_callback()
                self.start()
        if self.blink_sequence and self._started:
            if self.blink_timer.timeout == 'inf':
                self.blink_timer.set_timeout(self.blink_sequence.pop(0))
                self.blink_timer.reset()
                # self.blink_sequence.pop(0)
            elif self.blink_timer.tick:
                self.toggle_visibility()
                self.blink_timer.set_timeout(self.blink_sequence.pop(0))
                self.blink_timer.reset()

    def draw_points(self, points, surf, offset=(0, 0)):
        points = [
            [i[0] + offset[0], i[1] + offset[1]] for i in points
        ]
        if len(points) >= 2:
            pygame.draw.lines(surf, self.mask_color, False, points, 5)

    def draw(self, surf: pygame.Surface, offset):
        # pygame.draw.rect(surf, 'white', self.rect)
        if self._started and self.visible:
            if self.appear and not self.appear_sprite.done:
                image = self.appear_sprite.image
                image = pygame.transform.scale_by(image, self.size_scale)
                surf.blit(image,
                          (self.x + offset[0] - image.get_width() // 2, self.y + offset[1] - image.get_height() // 2))
                # self.appear_sprite.draw(surf)
            else:
                self.looping_sprite_sheet.draw(surf, self.x + offset[0], self.y + offset[1], size=self.size_scale)
        if self._draw_outline:
            points = self.outline[self.c + self.masking_offset: self.c + self.max_mask_length + self.masking_offset]
            self.draw_points(points, self.surf)
            points = self.outline[self.masking_offset - self.c - self.max_mask_length: self.masking_offset - self.c]
            self.draw_points(points, self.surf)
            if self.c + self.masking_offset >= len(self.outline):
                c = len(self.outline) - self.c
                points = self.outline[max(0, self.masking_offset - c - self.max_mask_length): self.masking_offset - c]
                self.draw_points(points, self.surf)
            surf.blit(self.surf, self.surf.get_rect(center=(self.x + offset[0], self.y + offset[1])))
            self.surf.fill((0, 0, 0, 10), special_flags=pygame.BLEND_RGBA_SUB)

    def draw_glow(self, surf: pygame.Surface, offset):
        r = max(self.rect.w, self.rect.h)
        g = get_radial_glow(r + math.sin(time.time() * 10) * 0, color='#D600C4')
        surf.blit(g, g.get_rect(center=(self.x + offset[0], self.y + offset[1])), special_flags=pygame.BLEND_RGB_MAX)


class ConnectedComponentSystem(BaseObject):
    def __init__(
            self,
            x, y,
            components_and_relative_pos: dict[Component, Sequence] = None,
            blink_sequence=()
    ):
        super(ConnectedComponentSystem, self).__init__(x, y)
        self.components = []
        if components_and_relative_pos is None:
            components_and_relative_pos = {}
        for i, j in components_and_relative_pos.items():
            i.pos = [x + j[0], y + j[1]]
            self.components.append(i)
        # self.components_and_relative_pos = components_and_relative_pos
        self.blink_timer = Timer('inf', reset=True)
        # self.blink_timer.set_callback(self.toggle_visibility)
        self.blink_sequence: list = list(blink_sequence)
        self.visible = True

    def toggle_visibility(self):
        self.visible = not self.visible

    def add_blink_sequence(self, *args, clear=False):
        if clear:
            self.blink_sequence = list(args)[1:]
            self.blink_timer = Timer(args[0])
        else:
            self.blink_sequence.extend(args)

    def has_component(self, label):
        return self.get_component(label) is not None

    def get_component(self, label):
        for i in self.components:
            if i.label == label:
                return i

    def move(self, dx, dy):
        for i in self.components:
            i.x += dx
            i.y += dy
        self.x += dx
        self.y += dy

    def move_to(self, x, y):
        dx, dy = x - self.x, y - self.y
        self.move(dx, dy)

    @property
    def rect(self) -> pygame.Rect:
        return self.components[0].rect.unionall([i.rect for i in self.components[1:]])

    def skip_intro_animations(self):
        for i in self.components:
            i.skip_to_start()
            self.blink_sequence.clear()

    def update(self, events: list[pygame.event.Event], dt):
        for i in self.components:
            i.update(events, dt)
        if self.blink_sequence:
            if self.blink_timer.timeout == 'inf':
                self.blink_timer.set_timeout(self.blink_sequence.pop(0))
                self.blink_timer.reset()
                # self.blink_sequence.pop(0)
            elif self.blink_timer.tick:
                self.toggle_visibility()
                self.blink_timer.set_timeout(self.blink_sequence.pop(0))
                self.blink_timer.reset()

    def draw(self, surf: pygame.Surface, offset):
        # pygame.draw.rect(surf, 'white', self.rect)
        if not self.visible:
            return
        for i in self.components:
            i.draw(surf, offset)

    def draw_glow(self, surf: pygame.Surface, offset):
        # return
        if not self.visible:
            return
        for i in self.components:
            i.draw_glow(surf, offset)


class AppearSprite(BaseObject):
    def __init__(self, sprite: pygame.Surface, vec=(0, 0), timer=0.1, speed=5):
        super().__init__()
        self.vec = vec
        self.timer = Timer(timer)
        self.speed = speed
        self.sprite = sprite
        self.surf = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
        self.c_x = 0
        self.c_v = 0
        self.x_done = False
        self.y_done = False

    def rect(self) -> pygame.Rect:
        return self.surf.get_rect()

    @property
    def done(self):
        return self.x_done and self.y_done

    @property
    def image(self):
        if self.x_done and self.y_done:
            return self.surf
        self.surf = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
        pos = [self.vec[0] * self.sprite.get_width(), self.vec[1] * self.sprite.get_height()]
        pos[0] -= self.c_x * self.vec[0]
        pos[1] -= self.c_v * self.vec[1]
        self.surf.blit(self.sprite, pos)
        return self.surf

    def skip(self):
        self.c_x = self.sprite.get_width()
        self.x_done = True
        self.c_v = self.sprite.get_height()
        self.y_done = True

    def update(self, events: list[pygame.event.Event], dt):
        if self.timer.tick:
            self.c_v += self.speed
            self.c_x += self.speed
            if self.c_x >= self.sprite.get_width():
                self.c_x = self.sprite.get_width()
                self.x_done = True
            if self.c_v >= self.sprite.get_height():
                self.c_v = self.sprite.get_height()
                self.y_done = True


class Particle(BaseObject):
    def __init__(self, x, y, size=5, vec=(0, 0)):
        super(Particle, self).__init__(x, y)
        self.size = size
        if isinstance(vec, tuple) or isinstance(vec, list):
            if vec == (0, 0):
                x = random.random()
                y = random.random()
                vec = [x * random.choice([-1, 1]), clamp(y, 0.9999, 1)]
        elif isinstance(vec, float) or isinstance(vec, int):
            angle = math.radians(vec)
            x = math.cos(angle)
            y = math.sin(angle)
            vec = [x, y]
        self.speed = random.randint(1, 5)
        vec = [vec[0] * self.speed, vec[1] * self.speed]
        self.dx, self.dy = vec

    def update(self, events: list[pygame.event.Event], dt):
        self.x += self.dx * dt
        self.x += random.random() * random.choice([1, -1]) * random.randint(0, self.speed) * dt
        self.y += self.dy * dt
        self.size -= 0.1 * dt
        if self.size <= 0:
            self.alive = False

    def draw(self, surf: pygame.Surface, offset):
        draw_circle(surf, 'white', (self.x, self.y), self.size)
        # pygame.draw.rect(surf, 'white', (self.x - self.size // 2, self.y - self.size // 2, self.size, self.size))


class TrailStamp(BaseObject):
    def __init__(self, x, y, surf: pygame.Surface, alpha_rate=20):
        super().__init__(x, y)
        self.surf = surf
        self.alpha = 255
        self.alpha_rate = alpha_rate

    def update(self, events: list[pygame.event.Event], dt):
        self.alpha -= self.alpha_rate * dt
        self.alpha = clamp(self.alpha, 0, 255)
        if self.alpha <= 0:
            self.alive = False
        else:
            self.surf.set_alpha(self.alpha)

    def draw(self, surf: pygame.Surface, offset):
        surf.blit(self.surf, self.surf.get_rect(center=self.pos))


class ObjectManager(BaseStructure):
    def __init__(self):
        self.objects: list[BaseObject] = []
        self._to_add: list[BaseObject] = []
        self.collision_enabled = True
        self.scene = None

    def get_object_count(self, instance):
        c = 0
        for i in self.objects:
            if type(i) == instance:
                c += 1
        return c

    def get_objects(self, instance):
        objects = []
        for i in self.objects:
            if type(i) == instance:
                objects.append(i)
        return objects

    def clear(self):
        self._to_add.clear()
        self.objects.clear()

    def add(self, _object: BaseObject):
        _object.object_manager = self
        self._to_add.append(_object)

    def add_multiple(self, _objects: list[BaseObject]):
        for i in _objects:
            self.add(i)

    def update(self, events: list[pygame.event.Event], dt):
        # PhysicsManager.update(events, dt)
        if self._to_add:
            self.objects.extend(self._to_add)
            self._to_add.clear()
        self.objects = [i for i in self.objects if i.alive]
        self.objects.sort(key=attrgetter('z'))
        for i in self.objects:
            i.update(events, dt)

    def draw(self, surf: pygame.Surface, offset):
        for i in self.objects:
            i.draw(surf, offset)
        # pygame.draw.rect(surf, 'black', self.player.rect, 2)

    def draw_glow(self, surf: pygame.Surface, offset=(0, 0)):
        for i in self.objects:
            i.draw_glow(surf, offset)
