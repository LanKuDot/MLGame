"""
The file for managing gameobjects in the scene
"""

import random

from pygame import Rect
from pygame.sprite import Group

from mlgame.utils.enum import StringEnum, auto

from .gameobject import Snake, Food

class GameStatus(StringEnum):
    GAME_OVER = auto()
    GAME_ALIVE = auto()

class Scene:
    """
    The main game scene
    """

    area_rect = Rect(0, 0, 300, 300)

    def __init__(self):
        self._create_scene()

        self.score = 0
        self._frame = 0
        self._status = GameStatus.GAME_ALIVE

    def _create_scene(self):
        """
        Import gameobjects to the scene and add them to the draw group
        """
        self._snake = Snake()
        self._food = Food()
        self._random_food_pos()

        self._draw_group = Group()
        self._draw_group.add(self._snake.head, *self._snake.body, self._food)

    def _random_food_pos(self):
        """
        Randomly set the position of the food
        """
        while True:
            candidate_pos = (
                random.randrange(0, Scene.area_rect.width, 10),
                random.randrange(0, Scene.area_rect.height, 10))

            if (candidate_pos != self._snake.head_pos and
                not self._snake.is_body_pos(candidate_pos)):
                break

        self._food.pos = candidate_pos

    def reset(self):
        self.score = 0
        self._frame = 0
        self._status = GameStatus.GAME_ALIVE

        self._snake = Snake()
        self._random_food_pos()
        self._draw_group.empty()
        self._draw_group.add(self._snake.head, *self._snake.body, self._food)

    def draw_gameobjects(self, surface):
        """
        Draw gameobjects to the given surface
        """
        self._draw_group.draw(surface)

    def update(self, action):
        """
        Update the scene

        @param action The action for controlling the movement of the snake
        """
        self._frame += 1
        self._snake.move(action)

        if self._snake.head_pos == self._food.pos:
            self.score += 1
            self._random_food_pos()
            new_body = self._snake.grow()
            self._draw_group.add(new_body)

        if (not Scene.area_rect.collidepoint(self._snake.head_pos) or
            self._snake.is_body_pos(self._snake.head_pos)):
            self._status = GameStatus.GAME_OVER

        return self._status

    def get_scene_info(self):
        """
        Get the current scene information
        """
        scene_info = {
            "frame": self._frame,
            "status": self._status.value,
            "snake_head": self._snake.head_pos,
            "snake_body": [body.pos for body in self._snake.body],
            "food": self._food.pos
        }

        return scene_info
