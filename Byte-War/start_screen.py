import pygame
from const import INTERFACE_UNIT, START_SCREEN_HEIGHT, START_SCREEN_WIDTH
from texture import generate_assets, textures
from interface import StartScreenInterface


class StartScreen:
    def __init__(self, app):
        self.screen = pygame.display.set_mode((START_SCREEN_WIDTH, START_SCREEN_HEIGHT))
        generate_assets()

        self.app = app
        self.background = textures["background"].copy()
        surface = pygame.Surface(
            (
                START_SCREEN_WIDTH - 2 * INTERFACE_UNIT,
                START_SCREEN_HEIGHT - 2 * INTERFACE_UNIT,
            ),
            pygame.SRCALPHA,
        )
        surface.fill((0, 0, 0, 224))
        self.background.blit(surface, (INTERFACE_UNIT, INTERFACE_UNIT))
        self.interface = StartScreenInterface(self)

    def update(self):
        self.interface.update()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.interface.draw(self.screen)
