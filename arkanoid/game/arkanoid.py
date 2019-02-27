import pygame
from . import gamecore

class Arkanoid():
	def __init__(self):
		self._init_pygame()
		self._frame = 0

	def _init_pygame(self):
		pygame.init()
		pygame.mixer.quit()	# Avoid unusual high CPU uage
		self._clock = pygame.time.Clock()
		self._screen = pygame.display.set_mode(gamecore.display_area_size)
		pygame.display.set_caption("Arkanoid")

	def game_loop(self, fps: int, level: int, log_dir: str = None):
		def keyboard_action() -> str:
			key_pressed_list = pygame.key.get_pressed()
			if key_pressed_list[pygame.K_LEFT]:
				return gamecore.ACTION_LEFT
			if key_pressed_list[pygame.K_RIGHT]:
				return gamecore.ACTION_RIGHT
			return gamecore.ACTION_NONE

		def check_going():
			for event in pygame.event.get():
				if event.type == pygame.QUIT or \
				  (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					return False
			return True

		scene = gamecore.Scene(level, True, self._screen)

		if log_dir is not None:
			from ..communication import SceneInfo
			from essential.recorder import Recorder
			recorder = Recorder(log_dir)
			def __record_scene_info(game_status):
				scene_info = scene.get_object_pos_info( \
					SceneInfo(self._frame, game_status))
				recorder.record_scene_info(scene_info)
			record_scene_info = __record_scene_info
		else:
			record_scene_info = lambda x: None

		game_status = gamecore.GAME_ALIVE_MSG

		while check_going():
			record_scene_info(game_status)
			control_action = keyboard_action()
			game_status = scene.update(control_action)
			self._frame += 1

			if game_status == gamecore.GAME_OVER_MSG or \
			   game_status == gamecore.GAME_PASS_MSG:
				record_scene_info(game_status)
				print(game_status)
				scene.reset()
				game_status = gamecore.GAME_ALIVE_MSG
				self._frame = 0
		
			scene.draw()
			pygame.display.flip()

			self._clock.tick(fps)

		pygame.quit()
