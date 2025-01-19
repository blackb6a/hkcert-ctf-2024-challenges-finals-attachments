import random
from interface_component import (
    ActionDisplay,
    ByteBox,
    ChatDisplay,
    ControlInfo,
    MainDisplay,
    MainInteractive,
    NameInputBox,
    PlayerTextureSelector,
    SideDisplay,
    TopDisplay,
)
import pygame
from texture import cursors


class Interface(pygame.sprite.Group):
    def __init__(self, context):
        self.context = context
        self.cursor_type = "default"
        super().__init__()

        self.buttons = pygame.sprite.Group()
        self.components = {}
        self.cursor_request = ["default"]

    @property
    def focusing(self):
        return any([c.focused for c in self.components.values()])

    def update(self):
        if self.focusing:
            for sprite in self.buttons:
                if sprite.is_hovered:
                    self.cursor_request.append("click")
                    if sprite.is_clicked:
                        sprite.on_click()

        super().update()
        self.buttons.update()
        self.update_cursor()

    def draw(self, screen):
        super().draw(screen)
        self.buttons.draw(screen)

    def update_component(self, component, hidden=None, data=None, force=False):
        if isinstance(component, str):
            component = self.components[component]
        if data is not None and (force or data != component.data):
            component.data = data
            component.pending_update = True
            component.update()
        if hidden is not None and hidden != component.hidden:
            if hidden:
                component.close()
            else:
                component.open()

    def update_cursor(self):
        new_cursors_type = self.cursor_request.pop()
        if new_cursors_type != self.cursor_type:
            self.cursor_type = new_cursors_type
            pygame.mouse.set_cursor(cursors[self.cursor_type])
        self.cursor_request = ["default"]


class SceneInterface(Interface):
    def __init__(self, context):
        super().__init__(context)
        self.components = {
            "byte_box": ByteBox(self),
            "top_display": TopDisplay(self),
            "main_display": MainDisplay(self),
            "main_interactive": MainInteractive(self),
            "action_display": ActionDisplay(self),
            "side_display": SideDisplay(self),
            "chat_display": ChatDisplay(self),
        }

    def update(self):
        base = self.context.base
        player = self.context.player

        # byte display
        if player.holdings is None:
            self.update_component("byte_box", hidden=True)
        else:
            self.update_component(
                "byte_box",
                data=self.context.tokens[player.holdings].value,
                hidden=False,
            )

        # top display
        self.update_component(
            "top_display",
            data=" ".join(map(lambda t: t.value, base.owned_tokens)),
            hidden=not base.has_player,
        )

        # action display
        available_actions = player.available_actions
        if len(available_actions) == 0:
            self.update_component("action_display", hidden=True)
        else:
            self.update_component(
                "action_display", data=available_actions[0], hidden=False
            )

        # side display
        self.update_component(
            "side_display", data=player.equipments, hidden=False, force=True
        )

        # chat display
        # TODO: extract update
        self.components["chat_display"].update_lines()

        # cursor for aiming
        if self.context.player.equipments.gun.active:
            self.cursor_request.append("aiming")

        super().update()


class StartScreenInterface(Interface):
    def __init__(self, context):
        super().__init__(context)
        self.components = {
            "selector": PlayerTextureSelector(self),
            "input_box": NameInputBox(self),
            "info": ControlInfo(self),
        }

        self.update_component(
            "selector", data=random.randint(0, 5), hidden=False, force=True
        )
        self.update_component("input_box", data="", hidden=False, force=True)
        self.update_component("info", hidden=False)
