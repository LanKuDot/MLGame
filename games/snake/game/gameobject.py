"""
The file for defining objects in the game
"""

from pygame import Rect, Surface, draw
from pygame.sprite import Sprite
from collections import deque

from mlgame.utils.enum import StringEnum, auto

class Food(Sprite):
    def __init__(self):
        super().__init__()

        self.rect = Rect(0, 0, 10, 10)

        surface = Surface(self.rect.size)
        draw.circle(surface, (232, 54, 42), self.rect.center, 5)

        self.image = surface

    @property
    def pos(self):
        return self.rect.topleft

    @pos.setter
    def pos(self, value):
        self.rect.topleft = value

class SnakeBody(Sprite):
    def __init__(self, init_pos, color):
        super().__init__()

        self.rect = Rect(init_pos[0], init_pos[1], 10, 10)

        width = self.rect.width
        height = self.rect.height

        self.image = Surface((width, height))
        self.image.fill(color)
        draw.line(self.image, (0, 0, 0), (width - 1, 0), (width - 1, height - 1))
        draw.line(self.image, (0, 0, 0), (0, height - 1), (width - 1, height - 1))

    @property
    def pos(self):
        return self.rect.topleft

    @pos.setter
    def pos(self, value):
        self.rect.topleft = value

class SnakeAction(StringEnum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    NONE = auto()

class Snake:
    def __init__(self):
        self.head = SnakeBody((40, 40), (31, 204, 42))  # Green

        self.body = deque()
        self.body_color = (255, 255, 255)   # White
        # Note the ordering of appending elements
        self.body.append(SnakeBody((40, 30), self.body_color))
        self.body.append(SnakeBody((40, 20), self.body_color))
        self.body.append(SnakeBody((40, 10), self.body_color))

        # Initialize the action to going down
        self._action = SnakeAction.DOWN

    @property
    def head_pos(self):
        return self.head.pos

    def is_body_pos(self, position):
        """
        Check if there has a snake body at the given position
        """
        for body in self.body:
            if body.pos == position:
                return True

        return False

    def grow(self):
        """
        Add a new snake body at the tail
        """
        new_body = SnakeBody(self.body[-1].pos, self.body_color)
        self.body.append(new_body)

        return new_body

    def move(self, action):
        """
        Move the snake according to the given action
        """
        # If there is no action, take the same action as the last frame.
        if action == SnakeAction.NONE:
            action = self._action

        # If the head will go back to the body,
        # take the same action as the last frame.
        possible_head_pos = self._get_possible_head_pos(action)
        if possible_head_pos == self.body[0].pos:
            action = self._action

        # Move the body 1 step ahead
        tail = self.body.pop()
        tail.pos = self.head.pos
        self.body.appendleft(tail)

        # Get the next head position according to the valid action
        next_head_pos = self._get_possible_head_pos(action)
        self.head.pos = next_head_pos

        # Store the action
        self._action = action

    def _get_possible_head_pos(self, action):
        """
        Get the possible head position according to the given action
        """
        if action == SnakeAction.UP:
            move_delta = (0, -10)
        elif action == SnakeAction.DOWN:
            move_delta = (0, 10)
        elif action == SnakeAction.LEFT:
            move_delta = (-10, 0)
        elif action == SnakeAction.RIGHT:
            move_delta = (10, 0)

        return self.head.rect.move(move_delta).topleft
