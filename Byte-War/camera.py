import random
import pygame
from const import SCREEN_HEIGHT, SCREEN_WIDTH


class Camera(pygame.sprite.Group):
    offset = pygame.Vector2(0, 0)

    def __init__(self, context):
        self.context = context
        super().__init__()

        self.effect = None

    def update(self):
        x, y = self.context.player.rect.center
        self.offset.x = x - SCREEN_WIDTH // 2
        self.offset.y = y - SCREEN_HEIGHT // 2

        if self.effect is not None:
            self.offset += next(self.effect, (0, 0))
        super().update()

    def draw(self, display: pygame.Surface):
        for sprite in self.sprites():
            pos = relative_position(sprite.rect)

            display.blit(sprite.image, pos)

    def start_vibration(self):
        self.effect = self.vibrate()

    def vibrate(self):
        for _ in range(10):
            yield (random.randint(-4, 4), random.randint(-4, 4))
        self.effect = None


def relative_position(rect: pygame.Rect):
    return pygame.Vector2(
        rect.x - Camera.offset.x,
        rect.y - Camera.offset.y,
    )
