import pygame
from . import gamecore
from .gamecore import GameStatus
from .gameobject import PlatformMoveAction

class PingPong:
	def __init__(self):
		self._init_pygame()

	def _init_pygame(self):
		pygame.display.init()
		self._clock = pygame.time.Clock()
		self._screen = pygame.display.set_mode(gamecore.display_area_size)
		pygame.display.set_caption("PingPong")

		pygame.font.init()
		self._font = pygame.font.Font(None, 22)
		self._font_pos_1P = (1, 4)
		self._font_pos_2P = (1, gamecore.display_area_size[1] - 21)
		self._font_pos_speed = (gamecore.display_area_size[0] - 75, \
			gamecore.display_area_size[1] - 21)

	def _check_going(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT or \
				(event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				return False
		return True

	def _keyboard_action(self):
		"""
		Get the action from the keyboard

		@return An action tuple (1P action, 2P action)
		"""
		action_1P = PlatformMoveAction.NONE
		action_2P = PlatformMoveAction.NONE

		key_pressed_list = pygame.key.get_pressed()
		if key_pressed_list[pygame.K_a]:
			action_1P = PlatformMoveAction.LEFT
		elif key_pressed_list[pygame.K_d]:
			action_1P = PlatformMoveAction.RIGHT

		if key_pressed_list[pygame.K_LEFT]:
			action_2P = PlatformMoveAction.LEFT
		elif key_pressed_list[pygame.K_RIGHT]:
			action_2P = PlatformMoveAction.RIGHT

		return action_1P, action_2P

	def game_loop(self, fps: int, game_over_score: int, \
		record_handler = lambda x: None):
		scene = gamecore.Scene(True, self._screen)

		while self._check_going():
			keyboard_action = self._keyboard_action()
			game_status = scene.update(*keyboard_action)

			if game_status == GameStatus.GAME_1P_WIN or \
				game_status == GameStatus.GAME_2P_WIN:
				print(game_status.name)
				if scene.score[0] == game_over_score or \
					scene.score[1] == game_over_score:
					break

				scene.reset()

			scene.draw()

			font_1P_surface = self._font.render( \
				"1P score: {}".format(scene.score[0]), True, gamecore.color_1P)
			font_2P_surface = self._font.render( \
				"2P score: {}".format(scene.score[1]), True, gamecore.color_2P)
			font_speed_surface = self._font.render( \
				"Speed: {}".format(abs(scene._ball._speed[0])), True, (255, 255, 255))
			self._screen.blit(font_1P_surface, self._font_pos_1P)
			self._screen.blit(font_2P_surface, self._font_pos_2P)
			self._screen.blit(font_speed_surface, self._font_pos_speed)

			pygame.display.flip()

			self._clock.tick(fps)

		if scene.score[0] > scene.score[1]:
			print("1P wins!")
		else:
			print("2P wins!")
		print("Final score: {}-{}".format(*scene.score))

		pygame.quit()
