import pygame
from const import ATLAS_TEXTURES, CURSORS, STANDALONE_TEXTURES, FONTS

fonts = {}
textures = {}
cursors = {}


def generate_standalone_textures():
    for name, data in STANDALONE_TEXTURES.items():
        if "path" not in data:
            textures[name] = pygame.Surface(
                (data["width"], data["height"]), pygame.SRCALPHA, 32
            ).convert_alpha()
            continue
        texture = pygame.image.load(data["path"]).convert_alpha()
        if "width" in data:
            texture = pygame.transform.scale(texture, (data["width"], data["height"]))
        if "scale" in data:
            texture = pygame.transform.scale_by(texture, data["scale"])
        textures[name] = texture


def generate_atlas_textures():
    for name, data in ATLAS_TEXTURES.items():
        atlas = pygame.image.load(data["path"]).convert_alpha()

        animation = data.get("animation")
        variants = data.get("variants")

        loaded_texture_name = []

        if variants is not None:
            suffixes = variants["suffixes"]
            rect, offset = variants["rect"], variants["offset"]

            for i, suffix in enumerate(suffixes):
                atlas_frame = atlas.subsurface(
                    pygame.Rect(
                        rect[0] + i * offset[0],
                        rect[1] + i * offset[1],
                        rect[2],
                        rect[3],
                    )
                )
                if animation is None:
                    if "width" in data:
                        atlas_frame = pygame.transform.scale(
                            atlas_frame, (data["width"], data["height"])
                        )
                    if "scale" in data:
                        atlas_frame = pygame.transform.scale_by(
                            atlas_frame, data["scale"]
                        )

                texture_name = f"{name}_{suffix}"
                textures[texture_name] = atlas_frame
                loaded_texture_name.append(texture_name)
        else:
            textures[name] = atlas
            loaded_texture_name = [name]

        if animation is not None:
            for texture_name in loaded_texture_name:
                atlas = textures[texture_name]
                loop, rect, offset = (
                    animation["loop"],
                    animation["rect"],
                    animation["offset"],
                )

                textures[texture_name] = []
                for i in range(loop):
                    atlas_frame = atlas.subsurface(
                        pygame.Rect(
                            rect[0] + i * offset[0],
                            rect[1] + i * offset[1],
                            rect[2],
                            rect[3],
                        )
                    )
                    if "width" in data:
                        atlas_frame = pygame.transform.scale(
                            atlas_frame, (data["width"], data["height"])
                        )
                    if "scale" in data:
                        atlas_frame = pygame.transform.scale_by(
                            atlas_frame, data["scale"]
                        )
                    textures[texture_name].append(atlas_frame)

                textures[texture_name + "_animation"] = {
                    "fps": animation["fps"],
                }


def generate_fonts():
    for name, font in FONTS.items():
        fonts[name] = pygame.font.Font(font["path"], font["size"])


def generate_cursors():
    for name, config in CURSORS.items():
        cursor_texture = textures[config["texture_name"]]
        cursors[name] = pygame.cursors.Cursor(config["hotspot"], cursor_texture)

    pygame.mouse.set_cursor(cursors["default"])


def generate_assets():
    textures["default"] = pygame.Surface((64, 64), pygame.SRCALPHA, 32).convert_alpha()
    generate_standalone_textures()
    generate_atlas_textures()
    generate_fonts()
    generate_cursors()
