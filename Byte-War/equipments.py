import pygame
from texture import textures
from map_object import AnimateObject
from const import BULLET_SPEED
from events import eventHandler
from utils import get_cooldown


class Bullet(AnimateObject):
    texture_name = "bullet"

    def __init__(self, context, init_data):
        self.context = context
        self.owner_id = init_data["owner_id"]
        self.velocity = pygame.Vector2()
        self.velocity.from_polar((BULLET_SPEED, init_data["angle"]))

        self.textures = []
        for texture in textures[self.texture_name]:
            self.textures.append(pygame.transform.rotate(texture, -init_data["angle"]))

        super().__init__(
            [context.groups["sprites"]],
            self.texture_name,
            {"center": init_data["position"]},
            lambda _, frame_num: self.textures[frame_num],
        )

        self.current_position = pygame.Vector2(self.rect.center)

    def update(self):
        self.move()
        super().update()

    def move(self):
        self.current_position += self.velocity
        self.rect.center = self.current_position
        if self.check_collision():
            self.kill()

    def check_collision(self):
        if self.rect.collidelist(self.context.groups["blocks"].sprites()) != -1:
            return True

        for player_id, base in self.context.bases.items():
            if player_id != self.owner_id and self.rect.colliderect(base):
                return True

        player = self.context.player
        if self.owner_id != player.id and self.rect.colliderect(player.rect):
            return True

        if (
            self.rect.collideobjects(
                [p for p in self.context.players.values() if p.id != self.owner_id],
                key=lambda p: p.rect,
            )
            is not None
        ):
            return True
        return False


class Barrier(AnimateObject):
    texture_name = "player_barrier"

    def __init__(self, groups, owner):
        super().__init__(groups, self.texture_name, {"center": owner.rect.center})
        self.owner = owner

    def update(self):
        super().update()
        self.rect = self.image.get_rect(center=self.owner.rect.center)


class PlayerEquipment:
    def __init__(self, level, active_after):
        self.active_after = active_after
        self.active = self.check_active()
        self.level = level
        self.base_cooldown = 5

    @property
    def cooldown(self):
        return get_cooldown(self.base_cooldown, self.level)

    @property
    def charge_percent(self):
        if self.active:
            return 1
        return 1 - (self.active_after - eventHandler.time) / self.cooldown

    @property
    def data(self):
        return {"level": self.level, "active_after": self.active_after}

    def check_active(self):
        return eventHandler.time > self.active_after

    def update(self, controller):
        new_active_state = self.check_active()
        if self.active != new_active_state:
            self.active = new_active_state

    def upgrade(self):
        self.level += 1

    def activate(self, args):
        pass

    def kill(self):
        pass

    def deactivate(self):
        self.active = False
        self.active_after = eventHandler.time + self.cooldown


class PlayerBarrier(PlayerEquipment):
    def __init__(self, level, active_after, owner):
        super().__init__(level, active_after)
        self.sprite = Barrier([], owner)
        self.active = False

    def update(self, controller):
        new_active_state = self.check_active()
        if self.active != new_active_state:
            if new_active_state:
                self.sprite.add(controller.context.groups["sprites"])
            else:
                self.sprite.kill()
            self.active = new_active_state

    def kill(self):
        self.sprite.kill()


class PlayerGun(PlayerEquipment):
    def __init__(self, level, active_after):
        super().__init__(level, active_after)

    def activate(self, args):
        if self.active:
            eventHandler.add_game_event("shoot", args)


class Equipments:
    def __init__(self, context, owner, init_data):
        self.context = context
        self.owner = owner

        self.shoe = PlayerEquipment(init_data["shoe"]["level"], 0)
        self.star = PlayerEquipment(init_data["star"]["level"], 0)
        self.barrier = PlayerBarrier(
            init_data["barrier"]["level"], init_data["barrier"]["active_after"], owner
        )
        self.gun = PlayerGun(
            init_data["gun"]["level"], init_data["gun"]["active_after"]
        )
        self.equipments = {
            "barrier": self.barrier,
            "shoe": self.shoe,
            "star": self.star,
            "gun": self.gun,
        }

    def __getitem__(self, key):
        return self.equipments.get(key)

    @property
    def data(self):
        return {name: equipment.data for name, equipment in self.equipments.items()}

    def update(self):
        for equipment in self.equipments.values():
            equipment.update(self)

    def kill(self):
        for equipment in self.equipments.values():
            equipment.kill()
