import string
import time
import pygame
from map_object import AnimateObject
from button import CancelButton, LeftButton, RightButton, SubmitButton, LoginButton
from texture import fonts, textures
from const import (
    INTERFACE_UNIT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    START_SCREEN_HEIGHT,
    START_SCREEN_WIDTH,
)
from utils import blit_text
from events import eventHandler


class InterfaceDisplay(pygame.sprite.Sprite):
    texture_name = "default"

    def __init__(self, interface):
        super().__init__()
        self.pending_update = False
        self.hidden = True
        self.buttons = {}
        self.data = None

        self.interface = interface

    @property
    def focused(self):
        return False

    def update(self):
        if self.pending_update:
            self.pending_update = False
            self.update_image()

    def update_image(self):
        pass

    def open(self):
        self.interface.add(self)
        for button in self.buttons.values():
            self.interface.buttons.add(button)
        self.hidden = False

    def close(self):
        self.interface.remove(self)
        for button in self.buttons.values():
            self.interface.buttons.remove(button)
        self.hidden = True


class ByteBox(InterfaceDisplay):
    texture_name = "byte_box"
    text_color = "white"
    font_name = "byte_display"

    def __init__(self, interface):
        super().__init__(interface)
        self.font = fonts[self.font_name]
        self.image = textures[self.texture_name]
        self.data = ""
        self.rect = self.image.get_rect(
            midbottom=(INTERFACE_UNIT * 1.5, SCREEN_HEIGHT + 30)
        )

    def update_image(self):
        text = self.font.render(self.data, True, self.text_color)
        frame = textures[self.texture_name].copy()
        frame.blit(text, text.get_rect(midtop=(frame.get_width() // 2, 19)))
        self.image = frame


class MainInteractive(InterfaceDisplay):
    texture_name = "main_interactive"
    text_color = "#4AEF26"
    text_color2 = "red"
    font_name = "main_display"
    prompt = "Submit your shellcode:\n"
    allowed_chars = "0123456789abcdefABCDEF"

    def __init__(self, interface):
        super().__init__(interface)
        self.font = fonts[self.font_name]
        self.image = textures[self.texture_name]
        self.rect = self.image.get_rect(midtop=(SCREEN_WIDTH // 2, INTERFACE_UNIT * 2))
        self.data = ""

        def on_submit():
            eventHandler.add_game_event("submit_code", {"code": self.data})
            self.close()

        x, y = self.rect.midbottom
        self.buttons["submit"] = SubmitButton(
            {"midbottom": (x * 2 // 3, y + 16)}, on_submit
        )
        self.buttons["cancel"] = CancelButton(
            {"midbottom": (x * 4 // 3, y + 16)}, self.close
        )

    @property
    def focused(self):
        return not self.hidden

    def update(self):
        self.text_input()
        super().update()

    def update_image(self):
        frame = textures[self.texture_name].copy()
        w, h = frame.get_size()
        text_start_pos = (64, 44)
        text_surface = frame.subsurface(
            (
                text_start_pos[0],
                text_start_pos[1],
                w - text_start_pos[0] * 2,
                h - text_start_pos[1] * 2,
            )
        )

        shellcode = " ".join(
            hhex + lhex for hhex, lhex in zip(self.data[::2], self.data[1::2])
        )
        shellcode += " "
        if len(self.data) % 2 != 0:
            shellcode += self.data[-1]

        available_bytes = self.interface.components["top_display"].data.split(" ") + [
            "0f",
            "05",
        ]

        def get_color(word, _):
            if len(word) == 2 and word.lower() not in available_bytes:
                return self.text_color2
            return self.text_color

        blit_text(
            text_surface,
            self.prompt + shellcode + "_",
            self.font,
            self.text_color,
            get_color,
        )

        self.image = frame

    def text_input(self):
        for event in eventHandler.events:
            if event.type == pygame.KEYDOWN:
                self.pending_update = True
                if event.key == pygame.K_BACKSPACE:
                    self.data = self.data[:-1]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.buttons["submit"].on_click()
                else:
                    if event.unicode in self.allowed_chars:
                        self.data += event.unicode.upper()


class MainDisplay(InterfaceDisplay):
    texture_name = "main_display"
    text_color = "#4AEF26"
    font_name = "main_display"

    def __init__(self, interface):
        super().__init__(interface)
        self.font = fonts[self.font_name]
        self.image = textures[self.texture_name]
        self.rect = self.image.get_rect(midtop=(SCREEN_WIDTH // 2, INTERFACE_UNIT * 2))
        self.data = ""

        x, y = self.rect.midbottom
        self.buttons["cancel"] = CancelButton({"midbottom": (x, y + 16)}, self.close)

    @property
    def focused(self):
        return not self.hidden

    def update_image(self):
        frame = textures[self.texture_name].copy()
        w, h = frame.get_size()
        text_start_pos = (64, 44)
        text_surface = frame.subsurface(
            (
                text_start_pos[0],
                text_start_pos[1],
                w - text_start_pos[0] * 2,
                h - text_start_pos[1] * 2,
            )
        )
        blit_text(text_surface, self.data, self.font, self.text_color)

        self.image = frame


class TopDisplay(InterfaceDisplay):
    texture_name = "top_display"
    text_color = "white"
    font_name = "top_display"

    def __init__(self, interface):
        super().__init__(interface)
        self.font = fonts[self.font_name]
        self.data = ""
        self.image = textures[f"{self.texture_name}_1"]
        self.rect = self.image.get_rect(midtop=(SCREEN_WIDTH // 2, 0))
        self.token_per_line = 24

    def update_image(self):
        chars_per_line = self.token_per_line * 3 - 1
        if len(self.data) <= chars_per_line:
            frame = textures[f"{self.texture_name}_1"].copy()
            text = self.font.render(self.data, True, self.text_color)
            frame.blit(text, text.get_rect(midtop=(frame.get_width() // 2, 40)))
            self.image = frame
        else:
            frame = textures[f"{self.texture_name}_2"].copy()
            text = self.font.render(self.data[:chars_per_line], True, self.text_color)
            frame.blit(text, text.get_rect(midtop=(frame.get_width() // 2, 40)))
            text = self.font.render(
                self.data[chars_per_line + 1 :], True, self.text_color
            )
            frame.blit(text, text.get_rect(midtop=(frame.get_width() // 2, 80)))
            self.image = frame


class ActionDisplay(InterfaceDisplay):
    texture_name = "action_frame"
    action_textures_map = {
        "pick": "action_pick",
        "drop": "action_drop",
        "investigate": "action_investigate",
    }

    def __init__(self, interface):
        super().__init__(interface)
        self.data = None
        self.image = textures[self.texture_name]
        self.rect = self.image.get_rect(
            midbottom=(SCREEN_WIDTH - INTERFACE_UNIT, SCREEN_HEIGHT)
        )

    def update_image(self):
        frame = textures[self.texture_name].copy()
        action_icon = textures[self.action_textures_map[self.data]]
        frame.blit(action_icon, action_icon.get_rect(center=frame.get_rect().center))
        self.image = frame


class SideDisplay(InterfaceDisplay):
    text_color = "white"
    background_color = "red"
    cooldown_color = "white"
    font_name = "side_display"
    texture_name = "side_frame"
    equipment_textures_map = {
        "gun": "equip_gun",
        "barrier": "equip_barrier",
        "shoe": "equip_shoe",
        "star": "equip_star",
    }

    def __init__(self, interface):
        super().__init__(interface)
        self.font = fonts[self.font_name]
        self.image = textures[self.texture_name]
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))

        self.texture_masks = {
            name: pygame.mask.from_surface(textures[texture_name])
            for name, texture_name in self.equipment_textures_map.items()
        }
        self.base_surface = pygame.Surface(
            textures[list(self.equipment_textures_map.values())[0]].get_size(),
            pygame.SRCALPHA,
        )
        self.base_surface.fill(self.background_color)

    def update_image(self):
        frame = textures[self.texture_name].copy()
        f_width, f_height = frame.get_size()
        for i, equipment_name in enumerate(self.equipment_textures_map):
            equipment = self.data[equipment_name]

            if equipment.active:
                texture = textures[self.equipment_textures_map[equipment_name]]
            else:
                s_width, s_height = self.base_surface.get_size()
                surface = self.base_surface.copy()

                surface.fill(
                    self.cooldown_color,
                    (0, 0, s_width, s_height * equipment.charge_percent),
                )
                texture = self.texture_masks[equipment_name].to_surface(
                    setsurface=surface, unsetcolor=(0, 0, 0, 0)
                )
            rect = texture.get_rect(midleft=(f_width * i // 4, f_height // 2)).move(
                20, 0
            )
            frame.blit(texture, rect)

            text = self.font.render(f"{equipment.level:02}", True, self.text_color)
            frame.blit(text, text.get_rect(midleft=(rect.move(8, 0).midright)))
        self.image = frame


class ChatDisplay(InterfaceDisplay):
    text_color = "white"
    font_name = "chat_display"
    texture_name = "chat_display"
    fade_time = 5

    def __init__(self, interface):
        super().__init__(interface)
        self.data = ""
        self.lines = []
        self.font = fonts[self.font_name]
        self.image = textures[self.texture_name]
        self.rect = self.image.get_rect(
            bottomleft=(0, SCREEN_HEIGHT - INTERFACE_UNIT * 1.5)
        )

        text_frame = self.image.copy()
        text_frame = pygame.transform.scale(
            text_frame, (self.rect.width, SCREEN_HEIGHT)
        )
        text_frame.fill((0, 0, 0, 64))
        self.text_frame = text_frame

    def update_lines(self):
        for line in list(self.lines):
            if line["fade_after"] < time.time():
                self.lines.remove(line)
                self.update_image()

    def update_image(self):
        frame = textures[self.texture_name].copy()
        frame_height = frame.get_height()

        if self.data:
            self.lines.append(self.analysis(self.data))
            self.data = ""
            height_sum = 0
            for i in range(len(self.lines) - 1, -1, -1):
                height_sum += self.lines[i]["height"]
                if height_sum > frame_height:
                    self.lines = self.lines[i:]
                    break

        if len(self.lines) != 0:
            text_frame, text_surface, _, h_offset = self.get_text_surface()

            _, rendered_height = blit_text(
                text_surface, self.get_text(), self.font, self.text_color
            )
            frame.blit(text_frame, (0, frame_height - rendered_height - h_offset))

        self.image = frame

    def analysis(self, data):
        surface_width = self.get_text_surface()[1].get_width()
        x, y = (0, 0)
        space_size = self.font.size(" ")[0]
        for word in data.split(" "):
            word_width, word_height = self.font.size(word)
            if x + word_width >= surface_width:
                x = 0
                y += word_height
            x += word_width + space_size
        x = 0
        y += word_height
        return {"text": data, "height": y, "fade_after": time.time() + self.fade_time}

    def get_text(self):
        text = ""
        for line in self.lines:
            text += line["text"] + "\n"
        return text

    def get_text_surface(self):
        text_frame = self.text_frame.copy()
        text_start_pos = (8, 8)
        w, h = text_frame.get_size()
        text_surface = text_frame.subsurface(
            (
                text_start_pos[0],
                text_start_pos[1],
                w - text_start_pos[0] * 2,
                h - text_start_pos[1] * 2,
            )
        )
        return text_frame, text_surface, text_start_pos[0], text_start_pos[1]


class PlayerTextureSelector(InterfaceDisplay):
    playerTextures = [
        "player1",
        "player2",
        "player3",
        "player4",
        "player5",
        "player6",
    ]

    def __init__(self, interface):
        super().__init__(interface)

        w, h = textures[f"{self.playerTextures[0]}_idle_down"][0].get_size()
        surface = pygame.Surface((w * 2, h), pygame.SRCALPHA)
        self.surface = surface
        self.image = surface
        self.rect = surface.get_rect(topleft=(INTERFACE_UNIT * 3, INTERFACE_UNIT * 2))
        self.data = 0
        self.frame_width = self.rect.w

        self.sprites = pygame.sprite.Group()
        self.textures = [
            AnimateObject(
                self.sprites,
                f"{player_texture}_idle_down",
                {"midtop": ((i + 0.5) * self.frame_width, 0)},
            )
            for i, player_texture in enumerate(self.playerTextures)
        ]

        def left():
            if not self.at_beginning:
                self.data -= 1
                self.buttons["right"].set_disabled(False)

            if self.at_beginning:
                self.buttons["left"].set_disabled(True)

        def right():
            if not self.at_end:
                self.data += 1
                self.buttons["left"].set_disabled(False)

            if self.at_end:
                self.buttons["right"].set_disabled(True)

        self.buttons["left"] = LeftButton({"midright": self.rect.midleft}, left)
        self.buttons["right"] = RightButton({"midleft": self.rect.midright}, right)
        self.buttons["left"].set_disabled(True)

    @property
    def at_beginning(self):
        return self.data == 0

    @property
    def at_end(self):
        return self.data == len(self.playerTextures) - 1

    @property
    def focused(self):
        return not self.hidden

    @property
    def current_texture(self):
        return self.playerTextures[self.data]

    def update(self):
        self.update_image()

    def update_image(self):
        current_midtop = self.textures[self.data].rect.midtop[0]
        target_midtop = 0.5 * self.frame_width
        if current_midtop != target_midtop:
            shift_x = (target_midtop - current_midtop) / 4
            if abs(shift_x) < 1:
                if shift_x > 0:
                    shift_x = 1
                else:
                    shift_x = -1
            for sprite in self.sprites:
                sprite.rect.move_ip((shift_x, 0))

        self.sprites.update()
        frame = self.surface.copy()
        self.sprites.draw(frame)
        self.image = frame


class NameInputBox(InterfaceDisplay):
    texture_name = "side_frame"
    text_color = "#4AEF26"
    font_name = "input_box"
    prompt = ">> "
    max_length = 32

    def __init__(self, interface):
        super().__init__(interface)
        self.font = fonts[self.font_name]
        self.image = textures[self.texture_name]
        self.rect = self.image.get_rect(
            topleft=(INTERFACE_UNIT * 2, INTERFACE_UNIT * 4)
        )
        self.data = ""

        def on_submit():
            if len(self.data) != self.max_length:
                return
            eventHandler.add_game_event(
                "login",
                {
                    "token": self.data,
                    "texture_name": interface.components["selector"].current_texture,
                },
            )
            interface.context.app.sync_once = True

        self.buttons["login"] = LoginButton(
            {"bottomright": self.rect.move(-8, -32).topright}, on_submit
        )
        self.buttons["login"].set_disabled(True)

    @property
    def focused(self):
        return not self.hidden

    def update(self):
        self.text_input()
        super().update()

    def update_image(self):
        if len(self.data) == self.max_length:
            self.buttons["login"].set_disabled(False)
        else:
            self.buttons["login"].set_disabled(True)

        self.image = textures[self.texture_name].copy()
        if self.data == "":
            text = "Team Token >> _"
        else:
            if (
                self.data.startswith("Invalid Token")
                and self.data.split("Invalid Token")[1] != ""
            ):
                self.data = self.data.removeprefix("Invalid Token")
            elif self.data.endswith("seconds") and self.data.split("seconds")[-1] != "":
                self.data = self.data.split("seconds")[-1]
            text = self.prompt + (self.data + "_")[: self.max_length]
        text_surface = self.font.render(text, True, self.text_color)
        self.image.blit(
            text_surface,
            text_surface.get_rect(midleft=(20, self.image.get_height() // 2)),
        )

    def text_input(self):
        for event in eventHandler.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                    if self.data == "Invalid Token":
                        self.data = ""
                    elif self.data.startswith("Wait ") and self.data.endswith(
                        "seconds"
                    ):
                        self.data = ""
                    clipboard = pygame.scrap.get("text/plain;charset=utf-8").decode()
                    self.data = (self.data + clipboard)[: self.max_length]
                    self.pending_update = True
                elif event.key == pygame.K_BACKSPACE:
                    if self.data == "Invalid Token":
                        self.data = ""
                    elif self.data.startswith("Wait ") and self.data.endswith(
                        "seconds"
                    ):
                        self.data = ""
                    else:
                        self.data = self.data[:-1]
                        self.pending_update = True
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.buttons["login"].on_click()
                elif len(self.data) < self.max_length:
                    if event.unicode in string.printable:
                        self.data += event.unicode
                        self.pending_update = True


class ControlInfo(InterfaceDisplay):
    title_font_name = "input_box"
    text_font_name = "main_display"
    text_color = "white"
    info = {
        "Move": ["key_a", "key_d", "key_w", "key_s"],
        "Interact": ["key_space"],
        "Quit": ["key_q"],
    }

    def __init__(self, interface):
        super().__init__(interface)
        surface = pygame.Surface(
            (
                START_SCREEN_WIDTH // 2 - 2 * INTERFACE_UNIT,
                START_SCREEN_HEIGHT - 3 * INTERFACE_UNIT,
            ),
            pygame.SRCALPHA,
        )

        fonts[self.title_font_name].set_underline(True)
        title_surface = fonts[self.title_font_name].render(
            "Controls", True, self.text_color
        )
        fonts[self.title_font_name].set_underline(False)
        surface.blit(
            title_surface,
            title_surface.get_rect(midtop=(surface.get_width() // 2, 0)),
        )

        start_pos = (INTERFACE_UNIT * 0.5, INTERFACE_UNIT * 1.5)
        for row, action in enumerate(self.info):
            text_surface = fonts[self.text_font_name].render(
                action, True, self.text_color
            )
            surface.blit(
                text_surface,
                text_surface.get_rect(
                    midleft=(start_pos[0], start_pos[1] + row * INTERFACE_UNIT)
                ),
            )
            keys = self.info[action]
            offset = 0
            for key in keys:
                key_texture = textures[key]
                surface.blit(
                    key_texture,
                    key_texture.get_rect(
                        midleft=(
                            start_pos[0] + 3 * INTERFACE_UNIT + offset,
                            start_pos[1] + row * INTERFACE_UNIT,
                        )
                    ),
                )
                offset += key_texture.get_width()

        self.image = surface
        self.rect = self.image.get_rect(
            midleft=(START_SCREEN_WIDTH // 2 + INTERFACE_UNIT, START_SCREEN_HEIGHT // 2)
        )
