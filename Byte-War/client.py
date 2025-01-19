from game import Game
import socket

from const import SERVER_HOST, SERVER_PORT


class Client:
    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_HOST, SERVER_PORT))
        s.settimeout(3)
        self.game = Game(s)

    def run(self):
        self.game.run()


if __name__ == "__main__":
    client = Client()
    client.run()
