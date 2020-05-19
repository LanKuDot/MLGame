GAME_VERSION = "1.0"
GAME_PARAMS = {
    "()": {
        "prog": "arkanoid",
        "game_usage": "%(prog)s <difficulty> <level>"
    },
    "difficulty": {
        "choices": ("EASY", "NORMAL"),
        "metavar": "difficulty",
        "help": "Specify the game style. Choices: %(choices)s"
    },
    "level": {
        "type": int,
        "help": "Specify the level map"
    }
}

from .game.arkanoid import Arkanoid
import pygame

GAME_SETUP = {
    "game": Arkanoid,
    "keyboards": [{
        pygame.K_a:     "SERVE_TO_LEFT",
        pygame.K_d:     "SERVE_TO_RIGHT",
        pygame.K_LEFT:  "MOVE_LEFT",
        pygame.K_RIGHT: "MOVE_RIGHT",
    }],
    "ml_clients": [
        { "name": "ml" }
    ]
}
