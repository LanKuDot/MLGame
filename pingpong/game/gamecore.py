import pygame
from enum import auto
from essential.game_base import StringEnum

from .gameobject import (
	Ball, Platform, PlatformMoveAction
)

display_area_size = (200, 500)	# (width, height)
color_1P = (84, 149, 255)	# Blue
color_2P = (219, 70, 92)	# Red

class GameStatus(StringEnum):
	GAME_1P_WIN = auto()
	GAME_2P_WIN = auto()
	GAME_ALIVE = auto()

class Scene:
	def __init__(self, display_on_screen: bool, screen = None):
		self._display_on_screen = display_on_screen
		self._screen = screen
		self._frame_count = 0
		self._game_status = GameStatus.GAME_ALIVE

		self.score = [0, 0]	# 1P, 2P

		self._create_scene()
		self.reset()

	def _create_scene(self):
		display_area_rect = pygame.Rect((0, 0), display_area_size)

		self._draw_group = pygame.sprite.RenderPlain()
		self._ball = Ball(display_area_rect, self._draw_group)
		self._platform_1P = Platform((85, 50), \
			display_area_rect, self._draw_group)
		self._platform_2P = Platform((85, display_area_size[1] - 60), \
			display_area_rect, self._draw_group)

		if self._display_on_screen:
			self._background = pygame.Surface(display_area_size)
			self._background.fill((0, 0, 0))
			self._ball.create_surface()
			self._platform_1P.create_surface(color_1P)
			self._platform_2P.create_surface(color_2P)

	def reset(self):
		self._frame_count = 0
		self._game_status = GameStatus.GAME_ALIVE
		self._ball.reset()
		self._platform_1P.reset()
		self._platform_2P.reset()

	def update(self, \
		move_action_1P: PlatformMoveAction, move_action_2P: PlatformMoveAction):
		self._frame_count += 1

		# Speed up the ball every 200 frames
		if self._frame_count % 200 == 0:
			self._ball.speed_up()

		self._ball.move()
		self._platform_1P.move(move_action_1P)
		self._platform_2P.move(move_action_2P)

		self._ball.check_bouncing(self._platform_1P, self._platform_2P)

		if self._ball.rect.bottom < self._platform_1P.rect.top:
			self._game_status = GameStatus.GAME_2P_WIN
			self.score[1] += 1
		elif self._ball.rect.top > self._platform_2P.rect.bottom:
			self._game_status = GameStatus.GAME_1P_WIN
			self.score[0] += 1
		else:
			self._game_status = GameStatus.GAME_ALIVE

		return self._game_status

	def draw(self):
		self._screen.blit(self._background, (0, 0))
		self._draw_group.draw(self._screen)
