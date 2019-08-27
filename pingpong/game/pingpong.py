import pygame

from . import gamecore
from .gamecore import GameStatus
from .gameobject import PlatformMoveAction
from ..communication import SceneInfo
from essential.gamedev.generic import quit_or_esc, KeyCommandMap

class PingPong:
	def __init__(self, fps: int, game_over_score: int , record_handler):
		self._init_pygame()

		self._fps = fps
		self._score = [0, 0]	# 1P, 2P
		self._game_over_score = game_over_score
		self._record_handler = record_handler
		self._scene = gamecore.Scene(True)
		self._keyboard_action_1P = KeyCommandMap({
			pygame.K_LEFT:  PlatformMoveAction.LEFT,
			pygame.K_RIGHT: PlatformMoveAction.RIGHT,
		}, PlatformMoveAction.NONE)
		self._keyboard_action_2P = KeyCommandMap({
			pygame.K_a: PlatformMoveAction.LEFT,
			pygame.K_d: PlatformMoveAction.RIGHT,
		}, PlatformMoveAction.NONE)

	def _init_pygame(self):
		pygame.display.init()
		pygame.display.set_caption("PingPong")
		self._screen = pygame.display.set_mode(gamecore.display_area_size)
		self._clock = pygame.time.Clock()

		pygame.font.init()
		self._font = pygame.font.Font(None, 22)
		self._font_pos_1P = (1, gamecore.display_area_size[1] - 21)
		self._font_pos_2P = (1, 4)
		self._font_pos_speed = (gamecore.display_area_size[0] - 75, \
			gamecore.display_area_size[1] - 21)

	def game_loop(self):
		while not quit_or_esc():
			command_1P = self._keyboard_action_1P.get_command()
			command_2P = self._keyboard_action_2P.get_command()

			scene_info = self._scene.fill_scene_info_obj(SceneInfo())
			scene_info.command_1P = command_1P.value
			scene_info.command_2P = command_2P.value
			self._record_handler(scene_info)

			game_status = self._scene.update(command_1P, command_2P)

			if game_status == GameStatus.GAME_1P_WIN or \
			   game_status == GameStatus.GAME_2P_WIN:
				print(game_status.value)
				self._record_handler(self._scene.fill_scene_info_obj(SceneInfo()))
				if self._game_over(game_status):
					break

				self._scene.reset()

			self._screen.fill((0, 0, 0))
			self._scene.draw_gameobjects(self._screen)
			self._draw_game_status()
			pygame.display.flip()

			self._clock.tick(self._fps)

		if self._score[0] > self._score[1]:
			print("1P wins!")
		else:
			print("2P wins!")
		print("Final score: {}-{}".format(*self._score))

		pygame.quit()

	def _draw_game_status(self):
		font_1P_surface = self._font.render( \
			"1P score: {}".format(self._score[0]), True, gamecore.color_1P)
		font_2P_surface = self._font.render( \
			"2P score: {}".format(self._score[1]), True, gamecore.color_2P)
		font_speed_surface = self._font.render( \
			"Speed: {}".format(abs(self._scene._ball._speed[0])), True, (255, 255, 255))
		self._screen.blit(font_1P_surface, self._font_pos_1P)
		self._screen.blit(font_2P_surface, self._font_pos_2P)
		self._screen.blit(font_speed_surface, self._font_pos_speed)

	def _game_over(self, status):
		if status == GameStatus.GAME_1P_WIN:
			self._score[0] += 1
		else:
			self._score[1] += 1

		is_game_over = self._score[0] == self._game_over_score or \
			self._score[1] == self._game_over_score

		return is_game_over