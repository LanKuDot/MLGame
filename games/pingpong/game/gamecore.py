import pygame
import random
from mlgame.utils.enum import StringEnum, auto

from .gameobject import (
    Ball, Blocker, Platform, PlatformAction, SERVE_BALL_ACTIONS
)

color_1P = (219, 70, 92)    # Red
color_2P = (84, 149, 255)    # Blue

class Difficulty(StringEnum):
    EASY = auto()
    NORMAL = auto()
    HARD = auto()

class GameStatus(StringEnum):
    GAME_1P_WIN = auto()
    GAME_2P_WIN = auto()
    GAME_DRAW = auto()
    GAME_ALIVE = auto()

class Scene:
    area_rect = pygame.Rect(0, 0, 200, 500)

    def __init__(self, difficulty: Difficulty):
        self._difficulty = difficulty
        self._frame_count = 0
        self._game_status = GameStatus.GAME_ALIVE
        self._ball_served = False
        self._ball_served_frame = 0

        self._create_scene()

    def _create_scene(self):
        self._draw_group = pygame.sprite.RenderPlain()

        enable_slice_ball = False if self._difficulty == Difficulty.EASY else True
        self._ball = Ball(Scene.area_rect, enable_slice_ball, self._draw_group)
        self._platform_1P = Platform((80, Scene.area_rect.height - 80),
            Scene.area_rect, "1P", color_1P, self._draw_group)
        self._platform_2P = Platform((80, 50),
            Scene.area_rect, "2P", color_2P, self._draw_group)
        if self._difficulty != Difficulty.HARD:
            # Put the blocker at the end of the world
            self._blocker = Blocker(1000, Scene.area_rect, self._draw_group)
        else:
            self._blocker = Blocker(240, Scene.area_rect, self._draw_group)

        # Initialize the position of the ball
        self._ball.stick_on_platform(self._platform_1P.rect, self._platform_2P.rect)

    def reset(self):
        self._frame_count = 0
        self._game_status = GameStatus.GAME_ALIVE
        self._ball_served = False
        self._ball_served_frame = 0
        self._ball.reset()
        self._platform_1P.reset()
        self._platform_2P.reset()
        self._blocker.reset()

        # Initialize the position of the ball
        self._ball.stick_on_platform(self._platform_1P.rect, self._platform_2P.rect)

    def update(self,
        move_action_1P: PlatformAction, move_action_2P: PlatformAction):
        self._frame_count += 1
        self._platform_1P.move(move_action_1P)
        self._platform_2P.move(move_action_2P)
        self._blocker.move()

        if not self._ball_served:
            self._wait_for_serving_ball(move_action_1P, move_action_2P)
        else:
            self._ball_moving()

        if self._ball.rect.top > self._platform_1P.rect.bottom:
            self._game_status = GameStatus.GAME_2P_WIN
        elif self._ball.rect.bottom < self._platform_2P.rect.top:
            self._game_status = GameStatus.GAME_1P_WIN
        elif abs(min(self._ball.speed, key = abs)) > 40:
            self._game_status = GameStatus.GAME_DRAW
        else:
            self._game_status = GameStatus.GAME_ALIVE

        return self._game_status

    def _wait_for_serving_ball(self, action_1P: PlatformAction, action_2P: PlatformAction):
        self._ball.stick_on_platform(self._platform_1P.rect, self._platform_2P.rect)

        target_action = action_1P if self._ball.serve_from_1P else action_2P

        # Force to serve the ball after 150 frames
        if (self._frame_count >= 150 and
            target_action not in SERVE_BALL_ACTIONS):
            target_action = random.choice(SERVE_BALL_ACTIONS)

        if target_action in SERVE_BALL_ACTIONS:
            self._ball.serve(target_action)
            self._ball_served = True
            self._ball_served_frame = self._frame_count

    def _ball_moving(self):
        # Speed up the ball every 200 frames
        if (self._frame_count - self._ball_served_frame) % 100 == 0:
            self._ball.speed_up()

        self._ball.move()
        self._ball.check_bouncing(self._platform_1P, self._platform_2P, self._blocker)

    def draw_gameobjects(self, surface):
        self._draw_group.draw(surface)

    def get_scene_info(self):
        """
        Get the scene information
        """
        scene_info = {
            "frame": self._frame_count,
            "status": self._game_status.value,
            "ball": self._ball.pos,
            "ball_speed": self._ball.speed,
            "platform_1P": self._platform_1P.pos,
            "platform_2P": self._platform_2P.pos
        }

        if self._difficulty == Difficulty.HARD:
            scene_info["blocker"] = self._blocker.pos

        return scene_info
