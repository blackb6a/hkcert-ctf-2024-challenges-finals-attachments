from equipments import Equipments
from map_object import AnimateObject, PlayerLabel


class OtherPlayer(AnimateObject):
    def __init__(self, context, init_data):
        self.id = init_data["id"]
        self.name = init_data["name"]
        self.direction = init_data["direction"]
        self.state = init_data["state"]
        self.texture_name = init_data["texture_name"]
        self.speed = init_data["speed"]
        self.holdings = init_data["holdings"]

        groups = [context.groups["sprites"]]

        super().__init__(
            groups,
            f"{self.texture_name}_{self.state}_{self.direction}",
            {"center": init_data["position"]},
        )

        self.name_plate = PlayerLabel(self, groups)
        self.equipments = Equipments(context, self, init_data["equipments"])

    @property
    def data(self):
        return {
            **self.__dict__,
            "position": self.rect.center,
            "equipments": self.equipments.data,
        }

    def update(self):
        self.equipments.update()

        self.current_texture_name = f"{self.texture_name}_{self.state}_{self.direction}"
        super().update()

    def kill(self):
        self.name_plate.kill()
        self.equipments.kill()
        super().kill()
