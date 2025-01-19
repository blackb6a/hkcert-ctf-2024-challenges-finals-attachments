import time
from const import TILE_SIZE


def map_tile_coordinates(position):
    return (position[1] // TILE_SIZE, position[0] // TILE_SIZE)


def map_tile_center(coordinates):
    return [
        int((coordinates[1] + 0.5) * TILE_SIZE),
        int((coordinates[0] + 0.5) * TILE_SIZE),
    ]


def blit_text(surface, text, font, color1, get_color=None):
    lines = [word.strip().split(" ") for word in text.splitlines()]
    space_size = font.size(" ")[0]
    surface_width, surface_height = surface.get_size()
    max_width = 0
    x, y = (0, 0)
    for line in lines:
        for word in line:
            color = color1
            if get_color is not None:
                color = get_color(word, line)
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= surface_width:
                x = 0
                y += word_height
            surface.blit(word_surface, (x, y))
            x += word_width + space_size
        max_width = max(max_width, x)
        x = 0
        y += word_height
    return [max_width, y]


def get_cooldown(base_time, level):
    return base_time * 100 / (100 + level * 20)


def token_reserved(t):
    return t["expired_at"] > time.time()
