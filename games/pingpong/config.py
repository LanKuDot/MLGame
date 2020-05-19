GAME_VERSION = "1.1"

from argparse import ArgumentTypeError

def positive_int(string):
    value = int(string)
    if value < 1:
        raise ArgumentTypeError()
    return value

GAME_PARAMS = {
    "()": {
        "prog": "pingpong",
        "game_usage": "%(prog)s <difficulty> [game_over_score]"
    },
    "difficulty": {
        "choices": ("EASY", "NORMAL", "HARD"),
        "metavar": "difficulty",
        "help": "Specify the game style. Choices: %(choices)s"
    },
    "game_over_score": {
        "type": positive_int,
        "nargs": "?",
        "default": 3,
        "help": ("[Optional] The score that the game will be exited "
            "when either side reaches it.[default: %(default)s]")
    }
}

from .game.pingpong import PingPong
import pygame

GAME_SETUP = {
    "game": PingPong,
    "keyboards": [{
        pygame.K_PERIOD: "SERVE_TO_LEFT",
        pygame.K_SLASH:  "SERVE_TO_RIGHT",
        pygame.K_LEFT:   "MOVE_LEFT",
        pygame.K_RIGHT:  "MOVE_RIGHT",
    }, {
        pygame.K_q: "SERVE_TO_LEFT",
        pygame.K_e: "SERVE_TO_RIGHT",
        pygame.K_a: "MOVE_LEFT",
        pygame.K_d: "MOVE_RIGHT",
    }],
    "ml_clients": [
        { "name": "ml_1P", "args": ("1P",) },
        { "name": "ml_2P", "args": ("2P",) }
    ]
}
