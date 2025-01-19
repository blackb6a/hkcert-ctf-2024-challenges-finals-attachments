import pygame
from map_object import AnimateObject, PlayerLabel
from events import eventHandler
from const import PLAYER_REACH, SCREEN_HEIGHT, SCREEN_WIDTH
from equipments import Equipments


class Player(AnimateObject):
    def __init__(self, context, init_data):
        self.context = context
        self.id = init_data["id"]
        self.texture_name = init_data["texture_name"]
        self.name = init_data["name"]
        self.state = init_data["state"]
        self.direction = init_data["direction"]
        self.speed = init_data["speed"]
        self.veclocity = pygame.Vector2()
        self.available_actions = []
        self.dirty_server_state = False
        groups = [context.groups["sprites"]]
        super().__init__(
            groups,
            f"{self.texture_name}_{self.state}_{self.direction}",
            {"center": init_data["position"]},
        )

        self.holdings = init_data["holdings"]
        self.equipments = Equipments(context, self, init_data["equipments"])
        self.name_plate = PlayerLabel(self, groups)

    @property
    def _state(self):
        new_state = ""
        if self.veclocity.magnitude() == 0:
            new_state = "idle"
        else:
            new_state = "walk"

        if self.state != new_state:
            self.animation_frame = self.animation_frame_len - 1
            self.tick_count = self.animation_interval - 1
            self.state = new_state

        return new_state

    @property
    def _direction(self):
        if self._state != "idle":
            if self.veclocity.x > 0:
                self.direction = "right"
            elif self.veclocity.x < 0:
                self.direction = "left"
            elif self.veclocity.y > 0:
                self.direction = "down"
            elif self.veclocity.y < 0:
                self.direction = "up"

        return self.direction

    @property
    def reachable_items(self):
        return self.rect.collideobjectsall(
            self.context.groups["pickables"].sprites(), key=lambda p: p.rect
        )

    @property
    def reachable_interactables(self):
        return list(filter(self.within_reach, self.context.groups["interactables"]))

    @property
    def data(self):
        return {
            **self.__dict__,
            "position": self.rect.center,
            "equipments": self.equipments.data,
        }

    def kill(self):
        self.name_plate.kill()
        self.equipments.kill()
        super().kill()

    def update(self):
        before_tainted = [self.direction, self.state, self.rect.center]

        self.equipments.update()

        if not self.context.interface.focusing:
            self.get_available_actions()
            self.input()
            self.move()

        self.current_texture_name = (
            f"{self.texture_name}_{self._state}_{self._direction}"
        )

        super().update()

        if before_tainted != [self.direction, self.state, self.rect.center]:
            eventHandler.add_game_event(
                "move",
                {
                    "direction": self.direction,
                    "state": self.state,
                    "position": self.rect.center,
                },
            )

    def move(self):
        self.rect.x += self.veclocity.x * self.speed
        self.check_collision("horizontal")
        self.rect.y += self.veclocity.y * self.speed
        self.check_collision("vertical")

    def input(self):
        if eventHandler.key_pressed(pygame.K_q):
            self.context.app.running = False
        if eventHandler.key_pressed(pygame.K_w):
            self.veclocity.y = -1
        if eventHandler.key_pressed(pygame.K_s):
            self.veclocity.y = 1
        if eventHandler.key_pressed(pygame.K_a):
            self.veclocity.x = -1
        if eventHandler.key_pressed(pygame.K_d):
            self.veclocity.x = 1

        if eventHandler.key_released(pygame.K_w):
            if self.context.app.key_state.get(pygame.K_s):
                self.veclocity.y = 1
            else:
                self.veclocity.y = 0
        if eventHandler.key_released(pygame.K_s):
            if self.context.app.key_state.get(pygame.K_w):
                self.veclocity.y = -1
            else:
                self.veclocity.y = 0
        if eventHandler.key_released(pygame.K_a):
            if self.context.app.key_state.get(pygame.K_d):
                self.veclocity.x = 1
            else:
                self.veclocity.x = 0
        if eventHandler.key_released(pygame.K_d):
            if self.context.app.key_state.get(pygame.K_a):
                self.veclocity.x = -1
            else:
                self.veclocity.x = 0
        if self.veclocity != (0, 0):
            self.veclocity.normalize_ip()

        if eventHandler.key_pressed(pygame.K_SPACE):
            if len(self.available_actions) > 0:
                match self.available_actions[0]:
                    case "pick":
                        item = self.reachable_items[0]
                        eventHandler.add_game_event("pick", {"id": item.id})
                    case "drop":
                        item = self.context.tokens[self.holdings]
                        eventHandler.add_game_event(
                            "drop", {"id": item.id, "position": self.rect.center}
                        )
                    case "investigate":
                        interactable = self.reachable_interactables[0]
                        interactable.interact(self)

        click_postion = eventHandler.mouse_clicked_at
        if click_postion is not None:
            shooting_angle = pygame.Vector2(
                click_postion[0] - SCREEN_WIDTH // 2,
                click_postion[1] - SCREEN_HEIGHT // 2,
            ).as_polar()[1]
            self.equipments.gun.activate({"angle": shooting_angle})

    def check_collision(self, direction):
        blocks = self.context.groups["blocks"].sprites()
        block_idx = self.rect.collidelist(blocks)

        if block_idx != -1:
            match direction:
                case "horizontal":
                    if self.veclocity.x > 0:
                        self.rect.right = blocks[block_idx].rect.left
                    if self.veclocity.x < 0:
                        self.rect.left = blocks[block_idx].rect.right
                case "vertical":
                    if self.veclocity.y > 0:
                        self.rect.bottom = blocks[block_idx].rect.top
                    if self.veclocity.y < 0:
                        self.rect.top = blocks[block_idx].rect.bottom

    def get_available_actions(self):
        available_actions = []
        # check investigate
        if len(self.reachable_interactables) > 0:
            available_actions.append("investigate")

        # check pick
        if (
            self.holdings is None
            and len(self.reachable_items) > 0
            and self.reachable_items[0].can_pick
        ):
            available_actions.append("pick")

        # check drop
        if (
            self.holdings is not None
            and len(self.reachable_items) == 0
            and self.context.tokens[self.holdings].can_drop
        ):
            available_actions.append("drop")

        self.available_actions = available_actions

    def within_reach(self, obj):
        return (
            pygame.Vector2(self.rect.center).distance_to(
                pygame.Vector2(obj.rect.center)
            )
            <= PLAYER_REACH
        )
