import pygame
from const import GAME_FPS, TILE_SIZE
from texture import textures, fonts


class SimpleMapObject(pygame.sprite.Sprite):
    def __init__(self, groups, texture_id, position):
        super().__init__(groups)
        self.image = textures[texture_id]
        self.rect = self.image.get_rect(**position)


class AnimateObject(pygame.sprite.Sprite):
    def __init__(self, groups, texture_name, position, get_image=None):
        super().__init__(groups)

        self.get_image = get_image
        self.current_texture_name = texture_name
        self.tick_count = 0
        self.animation_interval = None
        self.animation_frame = 0
        self.animation_frame_len = len(textures[self.current_texture_name])
        self.animation_interval = GAME_FPS // (
            min(textures[f"{self.current_texture_name}_animation"]["fps"], GAME_FPS)
        )

        if self.get_image is not None:
            self.image = self.get_image(texture_name, 0)
        else:
            self.image = textures[self.current_texture_name][0]

        self.rect = self.image.get_rect(**position)

    def update(self):
        self.tick_count = (self.tick_count + 1) % self.animation_interval
        if self.tick_count == 0:
            self.animation_frame = (self.animation_frame + 1) % self.animation_frame_len

            if self.get_image is not None:
                self.image = self.get_image(
                    self.current_texture_name, self.animation_frame
                )
            else:
                self.image = textures[self.current_texture_name][self.animation_frame]


class PlayerLabel(pygame.sprite.Sprite):
    font_name = "player_label"
    text_color = "white"
    max_line = 2
    max_char_per_line = 16

    def __init__(self, owner, groups):
        super().__init__(groups)
        self.owner = owner
        self.font = fonts[self.font_name]
        char_size_x, char_size_y = self.font.size("U")
        surface = pygame.Surface(
            (self.max_char_per_line * char_size_x, self.max_line * char_size_y),
            pygame.SRCALPHA,
        )

        label = owner.name
        for line, i in enumerate(range(0, len(label), self.max_char_per_line)):
            text = self.font.render(
                label[i : i + self.max_char_per_line], True, self.text_color
            )
            surface.blit(
                text,
                text.get_rect(midtop=(surface.get_width() // 2, line * char_size_y)),
            )

        self.image = surface
        self.rect = self.image.get_rect(midtop=self.owner.rect.midbottom)

    def update(self):
        self.rect = self.image.get_rect(midtop=self.owner.rect.midbottom)


class BaseInfoBoard(AnimateObject):
    def __init__(self, groups, id, coordinate, challenge_text=""):
        self.text = challenge_text
        super().__init__(
            groups, id, {"center": (coordinate[0], coordinate[1] - TILE_SIZE * 0.5)}
        )

    def interact(self, player):
        player.veclocity *= 0
        player.context.interface.update_component(
            "main_display", data=self.text, hidden=False
        )


class BaseTerminal(AnimateObject):
    def __init__(self, groups, id, coordinate):
        super().__init__(
            groups, id, {"midbottom": (coordinate[0], coordinate[1] + TILE_SIZE * 0.5)}
        )

    def interact(self, player):
        if player.context.base.has_player:
            player.veclocity *= 0
            player.context.interface.update_component(
                "main_interactive", data="", hidden=False
            )
