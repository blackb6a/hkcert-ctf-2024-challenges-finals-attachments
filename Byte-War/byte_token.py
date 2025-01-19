from utils import token_reserved
from map_object import AnimateObject


class Token(AnimateObject):
    texture_name = "byte_token"

    def __init__(self, context, init_data):
        self._groups = [context.groups["sprites"], context.groups["pickables"]]
        super().__init__(
            self._groups, self.texture_name, {"center": init_data["position"]}
        )
        self.id = init_data["id"]
        self.value = init_data["value"]
        self.expired_at = init_data["expired_at"]
        self.owner_id = init_data["owner_id"]

    def update(self):
        if token_reserved({"expired_at": self.expired_at}):
            self.current_texture_name = f"{self.texture_name}_reserved"
        else:
            self.current_texture_name = self.texture_name
        super().update()

    @property
    def can_pick(self):
        return self.owner_id is None and not token_reserved(
            {"expired_at": self.expired_at}
        )

    @property
    def can_drop(self):
        return self.owner_id is not None
