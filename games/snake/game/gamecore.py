"""
The file for managing gameobjects in the scene
"""

import random

from pygame import Rect
from pygame.sprite import Group

from mlgame.utils.enum import StringEnum

from .gameobject import Snake, Food

class GameStatus(StringEnum):
    GAME_OVER = "GAME_OVER"
    GAME_ALIVE = "GAME_ALIVE"

class SceneInfo:
    """
    The data structure for storing the scene information

    @var frame The number of frame for this scene information
    @var status The game status
    @var snake_head The position of the snake head
    @var snake_body A list of the position of snake bodies which
         are stored from the head (excluded) to the tail
    @var food The position of the food
    @var command The command used accroding to this scene information
    """

    def __init__(self):
        self.frame = 0
        self.status = GameStatus.GAME_ALIVE

        self.snake_head = (0, 0)
        self.snake_body = []
        self.food = (0, 0)

        self.command = None

    def __str__(self):
        output_str = \
            "# Frame {}\n".format(self.frame) + \
            "# Status {}\n".format(self.status.value) + \
            "# Snake Head {}\n".format(self.snake_head) + \
            "# Snake Body {}\n".format(' '.join(str(body) for body in self.snake_body)) + \
            "# Food {} \n".format(self.food) + \
            "# Command {}".format(self.command.value)

        return output_str

class Scene:
    """
    The main game scene
    """

    area_size = Rect(0, 0, 300, 300)

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
            candidate_pos = \
                (random.randrange(0, Scene.area_size.width, 10), \
                 random.randrange(0, Scene.area_size.height, 10))

            if candidate_pos != self._snake.head_pos and \
               not self._snake.is_body_pos(candidate_pos):
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

        if not Scene.area_size.collidepoint(self._snake.head_pos) or \
           self._snake.is_body_pos(self._snake.head_pos):
            self._status = GameStatus.GAME_OVER

        return self._status

    def get_scene_info(self):
        """
        Get the current scene information
        """
        scene_info = SceneInfo()

        scene_info.frame = self._frame
        scene_info.status = self._status
        scene_info.snake_head = self._snake.head_pos
        for body in self._snake.body:
            scene_info.snake_body.append(body.pos)
        scene_info.food = self._food.pos

        return scene_info
