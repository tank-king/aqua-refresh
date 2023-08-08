import asyncio

from src.engine.game import Game
from src.engine.utils import *

# import ez_profile

pygame.init()

if __name__ == '__main__':
    game = Game()
    asyncio.run(game.run())
