import pygame

from mlgame.gamedev.generic import quit_or_esc, KeyCommandMap
from mlgame.gamedev.recorder import get_record_handler

from . import gamecore
from ..communication import SceneInfo
from ..main import get_log_dir

class Arkanoid:
	def __init__(self, fps: int, level: int, record_progress, one_shot_mode):
		self._init_pygame()

		self._fps = fps
		self._scene = gamecore.Scene(level, True)
		self._keyboard = KeyCommandMap({
				pygame.K_LEFT:  gamecore.ACTION_LEFT,
				pygame.K_RIGHT: gamecore.ACTION_RIGHT,
			}, gamecore.ACTION_NONE)

		self._record_handler = get_record_handler(record_progress, {
				"status": (gamecore.GAME_OVER_MSG, gamecore.GAME_PASS_MSG)
			}, get_log_dir())
		self._one_shot_mode = one_shot_mode

	def _init_pygame(self):
		pygame.display.init()
		pygame.display.set_caption("Arkanoid")
		self._screen = pygame.display.set_mode(gamecore.scene_area_size)
		self._clock = pygame.time.Clock()

	def game_loop(self):
		while not quit_or_esc():
			self._record_handler(self._scene.fill_scene_info_obj(SceneInfo()))
			control_action = self._keyboard.get_command()
			game_status = self._scene.update(control_action)

			if game_status == gamecore.GAME_OVER_MSG or \
			   game_status == gamecore.GAME_PASS_MSG:
				print(game_status)
				self._record_handler(self._scene.fill_scene_info_obj(SceneInfo()))

				if self._one_shot_mode:
					return

				self._scene.reset()

			self._screen.fill((0, 0, 0))
			self._scene.draw_gameobjects(self._screen)
			pygame.display.flip()

			self._clock.tick(self._fps)

		pygame.quit()
