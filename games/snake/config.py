GAME_VERSION = "1.0"

from .game.snake import Snake
import pygame

GAME_SETUP = {
    "game": Snake,
    "keyboards": [{
        pygame.K_UP:    "UP",
        pygame.K_DOWN:  "DOWN",
        pygame.K_LEFT:  "LEFT",
        pygame.K_RIGHT: "RIGHT",
    }],
    "ml_clients": [
        { "name": "ml" }
    ]
}
