GAME_VERSION = "1.0"

from .game.snake import Snake
import pygame

GAME_SETUP = {
    "game": Snake,
    "ml_clients": [
        { "name": "ml" }
    ]
}
