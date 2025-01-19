import pygame


class Base:
    def __init__(self, context, rect=(0, 0, 0, 0)) -> None:
        self.context = context
        self.rect = pygame.Rect(rect)

    @property
    def owned_tokens(self):
        return self.rect.collideobjectsall(
            list(self.context.tokens.values()),
            key=lambda t: t.rect,
        )

    @property
    def has_player(self):
        return self.rect.colliderect(self.context.player.rect)
