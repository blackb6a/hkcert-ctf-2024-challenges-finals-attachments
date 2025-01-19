# game
START_SCREEN_WIDTH = 1280
START_SCREEN_HEIGHT = 480
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
INTERFACE_UNIT = SCREEN_HEIGHT // 15
TILE_SIZE = 96
GAME_FPS = 30
TOKEN_TTL = 60

# player
PLAYER_WIDTH = 54
PLAYER_HEIGHT = 90
PLAYER_SPEED = 12
PLAYER_REACH = TILE_SIZE
PLAYER_SHOE_BOOST = 6

# other
BULLET_SPEED = 30
EMULATOR_COOLDOWN = 10

# network
SERVER_HOST = "byte-war-hkcert24.pwnable.hk"
SERVER_PORT = 8888

# map
MAP_OBJECT = {
    "0": {
        "id": "wall",
        "type": "consecutive",
        "groups": ["sprites", "blocks"],
    },
    "1": {"id": "regular_floor", "type": "simple", "groups": ["sprites"]},
    "2": {"id": "base_floor", "type": "simple", "groups": ["sprites"]},
    "3u": {"id": "base_door_u", "type": "simple", "groups": ["sprites"]},
    "3l": {"id": "base_door_l", "type": "simple", "groups": ["sprites"]},
    "3r": {"id": "base_door_r", "type": "simple", "groups": ["sprites"]},
    "3d": {"id": "base_door_d", "type": "simple", "groups": ["sprites"]},
    "4": {
        "id": "base_info_board",
        "type": "base_info_board",
        "groups": ["sprites", "blocks", "interactables"],
    },
    "5": {
        "id": "base_terminal",
        "type": "base_terminal",
        "groups": ["sprites", "blocks", "interactables"],
    },
}

# fonts
FONTS = {
    "byte_display": {"path": "asset/font/DS-DIGIT.TTF", "size": 54},
    "top_display": {"path": "asset/font/DS-DIGIT.TTF", "size": 40},
    "side_display": {"path": "asset/font/DS-DIGIT.TTF", "size": 40},
    "main_display": {"path": "asset/font/chary.ttf", "size": 40},
    "chat_display": {"path": "asset/font/basis33.ttf", "size": 32},
    "player_label": {"path": "asset/font/basis33.ttf", "size": 28},
    "input_box": {"path": "asset/font/chary.ttf", "size": 32},
}

# cursors
CURSORS = {
    "default": {"texture_name": "cursor_default", "hotspot": (0, 0)},
    "click": {"texture_name": "cursor_click", "hotspot": (0, 0)},
    "aiming": {
        "texture_name": "cursor_aiming",
        "hotspot": (INTERFACE_UNIT // 4, INTERFACE_UNIT // 4),
    },
}

# texutres
ATLAS_TEXTURES = {
    "wall": {
        "path": "asset/walls.png",
        "width": TILE_SIZE,
        "height": TILE_SIZE,
        "variants": {
            "suffixes": [
                "t",
                "tb",
                "b",
                "r",
                "lr",
                "l",
                "br",
                "bl",
                "tr",
                "tl",
                "tbr",
                "tbl",
                "tlr",
                "blr",
                "tblr",
            ],
            "rect": (0, 0, 32, 32),
            "offset": (32, 0),
        },
    },
    "player1": {
        "path": "asset/char1.png",
        "width": PLAYER_WIDTH,
        "height": PLAYER_HEIGHT,
        "variants": {
            "suffixes": [
                "walk_down",
                "walk_left",
                "walk_right",
                "walk_up",
                "idle_down",
                "idle_left",
                "idle_right",
                "idle_up",
            ],
            "rect": (0, 0, 288, 72),
            "offset": (0, 72),
        },
        "animation": {
            "loop": 4,
            "rect": (18, 12, 36, 60),
            "offset": (72, 0),
            "fps": 5,
        },
    },
    "player2": {
        "path": "asset/char2.png",
        "width": PLAYER_WIDTH,
        "height": PLAYER_HEIGHT,
        "variants": {
            "suffixes": [
                "walk_down",
                "walk_left",
                "walk_right",
                "walk_up",
                "idle_down",
                "idle_left",
                "idle_right",
                "idle_up",
            ],
            "rect": (0, 0, 288, 72),
            "offset": (0, 72),
        },
        "animation": {
            "loop": 4,
            "rect": (18, 12, 36, 60),
            "offset": (72, 0),
            "fps": 5,
        },
    },
    "player3": {
        "path": "asset/char3.png",
        "width": PLAYER_WIDTH,
        "height": PLAYER_HEIGHT,
        "variants": {
            "suffixes": [
                "walk_down",
                "walk_left",
                "walk_right",
                "walk_up",
                "idle_down",
                "idle_left",
                "idle_right",
                "idle_up",
            ],
            "rect": (0, 0, 288, 72),
            "offset": (0, 72),
        },
        "animation": {
            "loop": 4,
            "rect": (18, 12, 36, 60),
            "offset": (72, 0),
            "fps": 5,
        },
    },
    "player4": {
        "path": "asset/char4.png",
        "width": PLAYER_WIDTH,
        "height": PLAYER_HEIGHT,
        "variants": {
            "suffixes": [
                "walk_down",
                "walk_left",
                "walk_right",
                "walk_up",
                "idle_down",
                "idle_left",
                "idle_right",
                "idle_up",
            ],
            "rect": (0, 0, 288, 72),
            "offset": (0, 72),
        },
        "animation": {
            "loop": 4,
            "rect": (18, 12, 36, 60),
            "offset": (72, 0),
            "fps": 5,
        },
    },
    "player5": {
        "path": "asset/char5.png",
        "width": PLAYER_WIDTH,
        "height": PLAYER_HEIGHT,
        "variants": {
            "suffixes": [
                "walk_down",
                "walk_left",
                "walk_right",
                "walk_up",
                "idle_down",
                "idle_left",
                "idle_right",
                "idle_up",
            ],
            "rect": (0, 0, 288, 72),
            "offset": (0, 72),
        },
        "animation": {
            "loop": 4,
            "rect": (18, 12, 36, 60),
            "offset": (72, 0),
            "fps": 5,
        },
    },
    "player6": {
        "path": "asset/char6.png",
        "width": PLAYER_WIDTH,
        "height": PLAYER_HEIGHT,
        "variants": {
            "suffixes": [
                "walk_down",
                "walk_left",
                "walk_right",
                "walk_up",
                "idle_down",
                "idle_left",
                "idle_right",
                "idle_up",
            ],
            "rect": (0, 0, 288, 72),
            "offset": (0, 72),
        },
        "animation": {
            "loop": 4,
            "rect": (18, 12, 36, 60),
            "offset": (72, 0),
            "fps": 5,
        },
    },
    "byte_token": {
        "path": "asset/card.png",
        "width": TILE_SIZE // 2,
        "height": TILE_SIZE // 2,
        "animation": {
            "loop": 8,
            "rect": (4, 4, 16, 16),
            "offset": (24, 0),
            "fps": 10,
        },
    },
    "byte_token_reserved": {
        "path": "asset/card_reserved.png",
        "width": TILE_SIZE // 2,
        "height": TILE_SIZE // 2,
        "animation": {
            "loop": 8,
            "rect": (4, 4, 16, 16),
            "offset": (24, 0),
            "fps": 10,
        },
    },
    "base_info_board": {
        "path": "asset/info_board.png",
        "scale": 2,
        "animation": {
            "loop": 4,
            "rect": (3, 8, 26, 16),
            "offset": (32, 0),
            "fps": 5,
        },
    },
    "base_terminal": {
        "path": "asset/terminal.png",
        "scale": 2,
        "animation": {
            "loop": 4,
            "rect": (6, 8, 18, 29),
            "offset": (32, 0),
            "fps": 5,
        },
    },
    "bullet": {
        "path": "asset/bullet.png",
        "scale": 4,
        "animation": {
            "loop": 4,
            "rect": (0, 0, 15, 6),
            "offset": (16, 0),
            "fps": 15,
        },
    },
    "player_barrier": {
        "path": "asset/barrier2.png",
        "width": PLAYER_HEIGHT + 12,
        "height": PLAYER_HEIGHT + 12,
        "animation": {
            "loop": 30,
            "rect": (0, 0, 421, 425),
            "offset": (421, 0),
            "fps": 30,
        },
    },
}

STANDALONE_TEXTURES = {
    "background": {
        "path": "asset/bg.jpg",
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
    },
    # map tiles
    "wall": {
        "path": "asset/wall.png",
        "width": TILE_SIZE,
        "height": TILE_SIZE,
    },
    "regular_floor": {
        # "path": "asset/reg_floor.png",
        "path": "asset/IndustrialTile_47.png",
        "width": TILE_SIZE,
        "height": TILE_SIZE,
    },
    "base_door_u": {
        "path": "asset/door_u.png",
        "width": TILE_SIZE,
        "height": TILE_SIZE,
    },
    "base_door_d": {
        "path": "asset/door_d.png",
        "width": TILE_SIZE,
        "height": TILE_SIZE,
    },
    "base_door_l": {
        "path": "asset/door_l.png",
        "width": TILE_SIZE,
        "height": TILE_SIZE,
    },
    "base_door_r": {
        "path": "asset/door_r.png",
        "width": TILE_SIZE,
        "height": TILE_SIZE,
    },
    "base_floor": {
        "path": "asset/base_floor.png",
        "width": TILE_SIZE,
        "height": TILE_SIZE,
    },
    # interface
    "byte_box": {
        "path": "asset/token_frame.png",
        "width": INTERFACE_UNIT * 2,
        "height": INTERFACE_UNIT * 2,
    },
    "top_display_1": {
        "path": "asset/top_frame_1.png",
        "width": SCREEN_WIDTH - INTERFACE_UNIT,
        "height": 113,
    },
    "top_display_2": {
        "path": "asset/top_frame_2.png",
        "width": SCREEN_WIDTH - INTERFACE_UNIT,
        "height": 2.5 * INTERFACE_UNIT,
    },
    "main_display": {
        "path": "asset/display_frame.png",
        "width": SCREEN_WIDTH - INTERFACE_UNIT * 2,
        "height": SCREEN_HEIGHT - INTERFACE_UNIT * 2.5,
    },
    "main_interactive": {
        "path": "asset/interactive_frame.png",
        "width": SCREEN_WIDTH - INTERFACE_UNIT * 2,
        "height": SCREEN_HEIGHT - INTERFACE_UNIT * 2.5,
    },
    "action_frame": {
        "path": "asset/action_frame.png",
        "width": INTERFACE_UNIT * 1.25,
        "height": INTERFACE_UNIT * 1.25,
    },
    "action_pick": {
        "path": "asset/action_pick.png",
        "width": INTERFACE_UNIT * 1.25,
        "height": INTERFACE_UNIT * 1.25,
    },
    "action_drop": {
        "path": "asset/action_drop.png",
        "width": INTERFACE_UNIT * 1.25,
        "height": INTERFACE_UNIT * 1.25,
    },
    "action_investigate": {
        "path": "asset/action_investigate.png",
        "width": INTERFACE_UNIT * 1.25,
        "height": INTERFACE_UNIT * 1.25,
    },
    "side_frame": {
        "path": "asset/sidebar.png",
        "width": INTERFACE_UNIT * 8.5,
        "height": INTERFACE_UNIT * 1.5,
    },
    "chat_display": {
        "width": INTERFACE_UNIT * 8,
        "height": INTERFACE_UNIT * 6,
    },
    "equip_shoe": {
        "path": "asset/shoe.png",
        "width": INTERFACE_UNIT / 4 * 3,
        "height": INTERFACE_UNIT / 4 * 3,
    },
    "equip_star": {
        "path": "asset/star.png",
        "width": INTERFACE_UNIT / 4 * 3,
        "height": INTERFACE_UNIT / 4 * 3,
    },
    "equip_barrier": {
        "path": "asset/barrier.png",
        "width": INTERFACE_UNIT / 4 * 3,
        "height": INTERFACE_UNIT / 4 * 3,
    },
    "equip_gun": {
        "path": "asset/gun.png",
        "width": INTERFACE_UNIT / 4 * 3,
        "height": INTERFACE_UNIT / 4 * 3,
    },
    "cancel_button": {
        "path": "asset/red_button.png",
        "width": SCREEN_HEIGHT // 12 * 4.375,
        "height": SCREEN_HEIGHT // 12,
    },
    "ok_button": {
        "path": "asset/green_button.png",
        "width": SCREEN_HEIGHT // 12 * 4.375,
        "height": SCREEN_HEIGHT // 12,
    },
    "left_button": {
        "path": "asset/left_button.png",
        "scale": 4,
    },
    "right_button": {
        "path": "asset/right_button.png",
        "scale": 4,
    },
    "left_button_disabled": {
        "path": "asset/left_button_disabled.png",
        "scale": 4,
    },
    "right_button_disabled": {
        "path": "asset/right_button_disabled.png",
        "scale": 4,
    },
    "login_button": {
        "path": "asset/green_button.png",
        "width": INTERFACE_UNIT * 2,
        "height": INTERFACE_UNIT * 1.5,
    },
    "login_button_disabled": {
        "path": "asset/grey_button.png",
        "width": INTERFACE_UNIT * 2,
        "height": INTERFACE_UNIT * 1.5,
    },
    # key
    "key_a": {"path": "asset/key_a.png", "scale": 4},
    "key_s": {"path": "asset/key_s.png", "scale": 4},
    "key_d": {"path": "asset/key_d.png", "scale": 4},
    "key_w": {"path": "asset/key_w.png", "scale": 4},
    "key_q": {"path": "asset/key_q.png", "scale": 4},
    "key_space": {"path": "asset/key_space.png", "scale": 4},
    # cursor
    "cursor_default": {"path": "asset/cursor3.png"},
    "cursor_click": {"path": "asset/cursor2.png"},
    "cursor_aiming": {
        "path": "asset/cursor_aiming5.png",
        "width": INTERFACE_UNIT // 2,
        "height": INTERFACE_UNIT // 2,
    },
}
