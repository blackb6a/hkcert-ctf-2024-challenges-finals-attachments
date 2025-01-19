import pygame
from const import GAME_FPS
from scene import Scene
from events import eventHandler
from other_player import OtherPlayer
from equipments import Bullet
from start_screen import StartScreen
from byte_token import Token


class Game:
    def __init__(self, conn):
        self.conn = conn

        pygame.init()
        pygame.display.set_caption("Byte War")
        pygame.scrap.init()
        pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

        self.running = True
        self.key_state = {}
        self.clock = pygame.time.Clock()
        self.login = False
        self.sync_once = False

        self.scene = StartScreen(self)

    def sync_from_server(self, conn):
        game_events = eventHandler.poll_game_events(conn)
        for event in game_events:
            body = event["body"]
            target = body.get("type")
            match event["command"]:
                case "error":
                    self.running = False
                    print(body["message"])
                case "reset":
                    self.login = True
                    self.scene = Scene(self, body)
                case "display":
                    match target:
                        case "interface":
                            self.scene.interface.update_component(
                                body["component"], data=body["message"], hidden=False
                            )
                        case "effect":
                            if body["name"] == "vibrate":
                                self.scene.groups["sprites"].start_vibration()
                        case "announcement":
                            self.scene.interface.update_component(
                                "chat_display", data=body["message"], hidden=False
                            )
                case "add":
                    match target:
                        case "player":
                            self.scene.players[body["id"]] = OtherPlayer(
                                self.scene, body
                            )
                        case "token":
                            self.scene.tokens[body["id"]] = Token(self.scene, body)
                        case "bullet":
                            Bullet(self.scene, body)
                case "remove":
                    match target:
                        case "player":
                            self.scene.players.pop(body["id"]).kill()
                        case "token":
                            self.scene.tokens.pop(body["id"]).kill()
                        case "bullet":
                            self.scene.bullets.pop(-1).kill()
                case "change":
                    match target:
                        case "player":
                            target = self.scene.players[body["id"]]
                        case "token":
                            target = self.scene.tokens[body["id"]]
                        case "self":
                            target = self.scene.player
                    for key, value in body.items():
                        match key:
                            case "id":
                                continue
                            case "position":
                                target.rect.center = value
                            case "equipments":
                                for equipment_name, equipment_data in value.items():
                                    equipment = target.equipments[equipment_name]
                                    for attr, data in equipment_data.items():
                                        setattr(equipment, attr, data)
                            case _:
                                setattr(target, key, value)

    def update(self):
        if self.login or self.sync_once:
            self.sync_from_server(self.conn)
            if self.sync_once:
                self.sync_once = False

        key_events = eventHandler.poll_events()
        for event in key_events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self.key_state[event.key] = True
            elif event.type == pygame.KEYUP:
                self.key_state[event.key] = False

        if not self.running:
            eventHandler.add_game_event("quit")

        self.scene.update()
        pygame.display.update()

        if self.login or self.sync_once:
            eventHandler.sync_game_events(self.conn)

    def draw(self):
        self.scene.draw()

    def close(self):
        pygame.quit()

    def run(self):
        while self.running:
            self.update()
            self.draw()

            self.clock.tick(GAME_FPS)

        self.close()
