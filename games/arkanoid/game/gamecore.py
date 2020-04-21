import pygame
import random

from mlgame.utils.enum import StringEnum, auto

from .gameobject import (
    Ball, Platform, Brick, HardBrick, PlatformAction, SERVE_BALL_ACTIONS
)

class Difficulty(StringEnum):
    EASY = auto()
    NORMAL = auto()

class GameStatus(StringEnum):
    GAME_ALIVE = auto()
    GAME_OVER = auto()
    GAME_PASS = auto()

class Scene:
    area_rect = pygame.Rect(0, 0, 200, 500)

    def __init__(self, difficulty, level):
        self._level = level
        self._difficulty = difficulty
        self._frame_count = 0
        self._game_status = GameStatus.GAME_ALIVE
        self._ball_served = False

        self._create_scene()

    def _create_scene(self):
        self._create_moves()
        self._create_bricks(self._level)

    def _create_moves(self):
        self._group_move = pygame.sprite.RenderPlain()
        enable_slide_ball = False if self._difficulty == Difficulty.EASY else True
        self._ball = Ball((93, 395), Scene.area_rect, enable_slide_ball, self._group_move)
        self._platform = Platform((75, 400), Scene.area_rect, self._group_move)

    def _create_bricks(self, level: int):
        def get_coordinate_and_type(string):
            string = string.rstrip("\n").split(' ')
            return int(string[0]), int(string[1]), int(string[2])

        self._group_brick = pygame.sprite.RenderPlain()
        self._brick_container = []

        import os.path
        dir_path = os.path.dirname(__file__)
        level_file_path = os.path.join(dir_path, "level_data/{0}.dat".format(level))

        with open(level_file_path, 'r') as input_file:
            offset_x, offset_y, _ = get_coordinate_and_type(input_file.readline())
            for input_pos in input_file:
                pos_x, pos_y, type = get_coordinate_and_type(input_pos.rstrip("\n"))
                BrickType = {
                    0: Brick,
                    1: HardBrick,
                }.get(type, Brick)

                brick = BrickType((pos_x + offset_x, pos_y + offset_y),
                    self._group_brick)
                self._brick_container.append(brick)

    def reset(self):
        self._frame_count = 0
        self._game_status = GameStatus.GAME_ALIVE
        self._ball_served = False
        self._ball.reset()
        self._platform.reset()
        self._group_brick.empty()
        self._group_brick.add(*self._brick_container)

        # Reset the HP of hard bricks
        for brick in self._brick_container:
            if isinstance(brick, HardBrick):
                brick.reset()

    def update(self, platform_action: PlatformAction) -> GameStatus:
        self._frame_count += 1
        self._platform.move(platform_action)

        if not self._ball_served:
            # Force to serve the ball after 150 frames
            if (self._frame_count >= 150 and
                platform_action not in SERVE_BALL_ACTIONS):
                platform_action = random.choice(SERVE_BALL_ACTIONS)

            self._wait_for_serving_ball(platform_action)
        else:
            self._ball_moving()

        if len(self._group_brick) == 0:
            self._game_status = GameStatus.GAME_PASS
        elif self._ball.rect.top >= self._platform.rect.bottom:
            self._game_status = GameStatus.GAME_OVER
        else:
            self._game_status = GameStatus.GAME_ALIVE

        return self._game_status

    def _wait_for_serving_ball(self, platform_action: PlatformAction):
        self._ball.stick_on_platform(self._platform.rect.centerx)

        if platform_action in SERVE_BALL_ACTIONS:
            self._ball.serve(platform_action)
            self._ball_served = True

    def _ball_moving(self):
        self._ball.move()

        self._ball.check_hit_brick(self._group_brick)
        self._ball.check_bouncing(self._platform)

    def draw_gameobjects(self, surface):
        self._group_brick.draw(surface)
        self._group_move.draw(surface)

    def get_scene_info(self) -> dict:
        """
        Get the scene information
        """
        scene_info = {
            "frame": self._frame_count,
            "status": self._game_status.value,
            "ball": self._ball.pos,
            "platform": self._platform.pos,
            "bricks": [],
            "hard_bricks": []
        }

        for brick in self._group_brick:
            if isinstance(brick, HardBrick) and brick.hp == 2:
                scene_info["hard_bricks"].append(brick.pos)
            else:
                scene_info["bricks"].append(brick.pos)

        return scene_info

    @property
    def catch_ball_times(self) -> int:
        return self._ball.hit_platform_times
