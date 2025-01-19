from const import SCREEN_HEIGHT, SCREEN_WIDTH
import pygame
from base import Base
from map import Map
from player import Player
from camera import Camera
from interface import SceneInterface
from byte_token import Token
from other_player import OtherPlayer
from texture import textures


class Scene:
    def __init__(self, app, init_data):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        current_player = init_data["current_player"]
        player_data = init_data["players"].pop(current_player)
        tokens_data = init_data["tokens"]
        other_players_data = init_data["players"]
        map_data = init_data["map_data"]
        self.challenge_text = init_data["challenge_text"]
        self.bases = init_data["bases"]

        self.tokens = {}
        self.players = {}
        self.bullets = []
        self.app = app

        self.groups = {
            "sprites": Camera(self),
            "blocks": pygame.sprite.Group(),
            "pickables": pygame.sprite.Group(),
            "interactables": pygame.sprite.Group(),
        }
        self.map = Map(self, map_data)
        self.base = Base(self, player_data["base_rect"])
        self.player = Player(self, player_data)
        self.interface = SceneInterface(self)

        self.generate_tokens(tokens_data)
        self.generate_other_players(other_players_data)

    def update(self):
        self.groups["sprites"].update()
        self.interface.update()

    def draw(self):
        self.screen.blit(textures["background"], (0, 0))
        self.groups["sprites"].draw(self.screen)
        self.interface.draw(self.screen)

    def generate_tokens(self, tokens_data):
        for token_id, token_data in tokens_data.items():
            self.tokens[token_id] = Token(self, token_data)

    def generate_other_players(self, players_data):
        for player_ip, player_data in players_data.items():
            self.players[player_ip] = OtherPlayer(self, player_data)
