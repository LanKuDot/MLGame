import pygame
from . import gamecore

class Arkanoid():
	def __init__(self):
		self._init_pygame()

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
			def __record_scene_info():
				scene_info = scene.fill_scene_info_obj(SceneInfo())
				recorder.record_scene_info(scene_info)
			record_scene_info = __record_scene_info
		else:
			record_scene_info = lambda: None	# Dummy function

		while check_going():
			record_scene_info()
			control_action = keyboard_action()
			game_status = scene.update(control_action)

			if game_status == gamecore.GAME_OVER_MSG or \
			   game_status == gamecore.GAME_PASS_MSG:
				print(game_status)
				record_scene_info()
				scene.reset()
		
			scene.draw()
			pygame.display.flip()

			self._clock.tick(fps)

		pygame.quit()
