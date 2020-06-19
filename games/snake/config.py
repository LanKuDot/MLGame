GAME_VERSION = "1.0"
GAME_PARAMS = {
    "()": {
        "prog": "snake",
        "description": "A simple snake game",
        "game_usage": "%(prog)s"
    }
}

from .game.snake import Snake

GAME_SETUP = {
    "game": Snake,
    "ml_clients": [
        { "name": "ml" }
    ]
}
