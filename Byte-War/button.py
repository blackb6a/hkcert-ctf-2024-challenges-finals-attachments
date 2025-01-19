import pygame
from texture import fonts, textures
from events import eventHandler


class Button(pygame.sprite.Sprite):
    text_color = "white"
    font_name = "main_display"

    def __init__(self, texture_name, position, button_label=None, callback=None):
        super().__init__()

        self.callback = callback
        self.label = button_label
        self.texture_name = texture_name
        self.image = None
        self.disable = False
        self.set_disabled(False)
        self.rect = self.image.get_rect(**position)

    @property
    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    @property
    def is_clicked(self):
        return self.is_hovered and eventHandler.mouse_clicked_at is not None

    def on_click(self):
        if not self.disable and self.callback is not None:
            self.callback()

    def set_disabled(self, disabled):
        self.disable = disabled
        if disabled:
            frame = textures[f"{self.texture_name}_disabled"].copy()
        else:
            frame = textures[self.texture_name].copy()

        if self.label is not None:
            text = fonts[self.font_name].render(self.label, True, self.text_color)
            frame.blit(text, text.get_rect(center=frame.get_rect().center))

        self.image = frame


class SubmitButton(Button):
    button_label = "Submit"
    texture_name = "ok_button"

    def __init__(self, position, callback=None):
        super().__init__(self.texture_name, position, self.button_label, callback)


class CancelButton(Button):
    button_label = "Cancel"
    texture_name = "cancel_button"

    def __init__(self, position, callback=None):
        super().__init__(self.texture_name, position, self.button_label, callback)


class LeftButton(Button):
    texture_name = "left_button"

    def __init__(self, position, callback=None):
        super().__init__(self.texture_name, position, callback=callback)


class RightButton(Button):
    texture_name = "right_button"

    def __init__(self, position, callback=None):
        super().__init__(self.texture_name, position, callback=callback)


class LoginButton(Button):
    button_label = "Login"
    texture_name = "login_button"

    def __init__(self, position, callback=None):
        super().__init__(self.texture_name, position, self.button_label, callback)
