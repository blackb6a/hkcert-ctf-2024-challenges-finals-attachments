from map_object import SimpleMapObject, BaseInfoBoard, BaseTerminal
from const import MAP_OBJECT
from utils import map_tile_center, map_tile_coordinates


class Map:
    def __init__(self, context, init_data):
        self.context = context
        self.generate_map(init_data)

    def generate_map(self, map_ids):
        for row_idx, row in enumerate(map_ids):
            for col_idx, object_ids in enumerate(row):
                for object_id in object_ids:
                    object_data = MAP_OBJECT[object_id]
                    texture_id = object_data["id"]
                    position = map_tile_center((row_idx, col_idx))
                    _groups = [
                        self.context.groups[group] for group in object_data["groups"]
                    ]
                    match object_data["type"]:
                        case ("simple" | "consecutive") as obj_type:
                            if obj_type == "consecutive":
                                texture_id += "_"
                                on_first_row = row_idx == 0
                                on_last_row = row_idx == len(map_ids) - 1
                                on_first_col = col_idx == 0
                                on_last_col = col_idx == len(row) - 1

                                if (
                                    not on_first_row
                                    and object_id in map_ids[row_idx - 1][col_idx]
                                ):
                                    texture_id += "t"
                                if (
                                    not on_last_row
                                    and object_id in map_ids[row_idx + 1][col_idx]
                                ):
                                    texture_id += "b"
                                if (
                                    not on_first_col
                                    and object_id in map_ids[row_idx][col_idx - 1]
                                ):
                                    texture_id += "l"
                                if (
                                    not on_last_col
                                    and object_id in map_ids[row_idx][col_idx + 1]
                                ):
                                    texture_id += "r"
                                if texture_id[-1] == "_":
                                    texture_id = texture_id[:-1]

                            SimpleMapObject(_groups, texture_id, {"center": position})
                        case "base_info_board":
                            BaseInfoBoard(
                                _groups,
                                texture_id,
                                position,
                                challenge_text=self.context.challenge_text,
                            )
                        case "base_terminal":
                            BaseTerminal(_groups, texture_id, position)
                        case _:
                            raise ValueError(
                                f"Unknown object type: {object_data['type']}"
                            )
