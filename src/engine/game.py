import asyncio
from pathlib import Path

import pygame

from src.engine.config import *
from src.engine.scene import SceneManager
from src.engine.sounds import SoundManager
from src.engine.utils import clamp, text

parent = Path(__file__).parent
sys.path.append(parent.absolute().__str__())
#
try:
    pygame.mixer.init()
    pygame.mixer.set_num_channels(16)
    Globals.set_global('speakers_init', True)
    SoundManager.load_sounds()
except pygame.error:
    Globals.set_global('speakers_init', False)
    try:
        pygame.init()
    except pygame.error:
        pass


#
# SoundManager.load_sounds()
#
# pygame.key.set_repeat(500, 50)

pygame.init()


class Game:
    def __init__(self):
        flags = pygame.SCALED | pygame.FULLSCREEN
        full_screen = False
        if full_screen:
            self.screen = pygame.display.set_mode([WIDTH, HEIGHT], flags)
        else:
            self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(GAME_NAME)
        # pygame.key.set_repeat(500, 10)
        self.full_screen = False
        self.manager = SceneManager()
        self.clock = pygame.time.Clock()
        SoundManager.play_bg('bg.wav')

    def toggle_full_screen(self):
        self.full_screen = not self.full_screen
        if self.full_screen:
            self.screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.SCALED | pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode([WIDTH, HEIGHT])

    async def run(self):
        dt = 1
        fps = 60
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    sys.exit(0)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_f:
                        self.toggle_full_screen()
                    # if e.key == pygame.K_ESCAPE:
                    #     sys.exit(0)
                    if e.key == pygame.K_c:
                        if fps == 60:
                            fps = 0
                        else:
                            fps = 60
            await asyncio.sleep(0)
            self.manager.update(events, dt)
            self.manager.draw(self.screen, (0, 0))
            t = text(int(self.clock.get_fps()).__str__(), color='black')
            # t = text("Hi All!", color='black', size=50)
            # self.screen.blit(t, [0, 0])
            pygame.display.update()
            SoundManager.update()
            self.clock.tick(fps)
            try:
                dt = TARGET_FPS / self.clock.get_fps()
            except ZeroDivisionError:
                dt = 1
            dt = clamp(dt, 0.1, 2)
