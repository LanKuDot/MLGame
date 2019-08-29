import pygame
from mlgame.utils.enum import StringEnum

from .gameobject import (
	Ball, Platform, PlatformMoveAction
)

display_area_size = (200, 500)	# (width, height)
color_1P = (219, 70, 92)	# Red
color_2P = (84, 149, 255)	# Blue

class GameStatus(StringEnum):
	GAME_1P_WIN = "GAME_1P_WIN"
	GAME_2P_WIN = "GAME_2P_WIN"
	GAME_ALIVE = "GAME_ALIVE"

class Scene:
	def __init__(self, to_create_surface: bool):
		self._to_create_surface = to_create_surface
		self._frame_count = 0
		self._game_status = GameStatus.GAME_ALIVE

		self._create_scene()
		self.reset()

	def _create_scene(self):
		display_area_rect = pygame.Rect((0, 0), display_area_size)

		self._draw_group = pygame.sprite.RenderPlain()
		self._ball = Ball(display_area_rect, self._draw_group)
		self._platform_1P = Platform((80, display_area_size[1] - 80), \
			display_area_rect, self._draw_group)
		self._platform_2P = Platform((80, 50), \
			display_area_rect, self._draw_group)

		if self._to_create_surface:
			self._ball.create_surface()
			self._platform_1P.create_surface("1P", color_1P)
			self._platform_2P.create_surface("2P", color_2P)

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

		if self._ball.rect.top > self._platform_1P.rect.bottom:
			self._game_status = GameStatus.GAME_2P_WIN
		elif self._ball.rect.bottom < self._platform_2P.rect.top:
			self._game_status = GameStatus.GAME_1P_WIN
		else:
			self._game_status = GameStatus.GAME_ALIVE

		return self._game_status

	def draw_gameobjects(self, surface):
		self._draw_group.draw(surface)

	def fill_scene_info_obj(self, scene_info_obj):
		"""
		Fill the information of the scene to the `scene_info_obj`
		"""
		def get_pivot_point(rect):
			return (rect.x, rect.y)

		scene_info_obj.frame = self._frame_count
		scene_info_obj.status = self._game_status.value
		scene_info_obj.ball = get_pivot_point(self._ball.rect)
		scene_info_obj.ball_speed = abs(self._ball._speed[0])
		scene_info_obj.platform_1P = get_pivot_point(self._platform_1P.rect)
		scene_info_obj.platform_2P = get_pivot_point(self._platform_2P.rect)

		return scene_info_obj
