import json
import time
import pygame


class EventHandler(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.time = 0
        self.events = []
        self.game_events = []
        self.game_events_locked = False

    def add_game_event(self, command, body=None):
        self.game_events.append({"command": command, "body": body})

    def sync_game_events(self, conn):
        conn.send(json.dumps(self.game_events).encode("utf-8"))
        self.game_events = []

    def poll_game_events(self, conn):
        data = b""
        for _ in range(10):
            data += conn.recv(65536)
            if len(data) == 0:
                break
            try:
                return json.loads(data)
            except json.decoder.JSONDecodeError:
                pass
            except:
                break
        print("Disconnected from server")
        exit(0)

    def poll_events(self):
        self.events = pygame.event.get()
        self.time = time.time()
        return self.events

    def key_pressed(self, key):
        for event in self.events:
            if event.type == pygame.KEYDOWN and event.key == key:
                return True
        return False

    def key_released(self, key):
        for event in self.events:
            if event.type == pygame.KEYUP and event.key == key:
                return True
        return False

    @property
    def mouse_clicked_at(self):
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return event.pos
        return None


eventHandler = EventHandler()
