import pygame, os
from . import gameobject

display_area_size = (200, 500)	# (width, height)

GAME_ALIVE_MSG = "GAME_ALIVE"
GAME_OVER_MSG = "GAME_OVER"
GAME_PASS_MSG = "GAME_PASS"

ACTION_LEFT = "LEFT"
ACTION_RIGHT = "RIGHT"
ACTION_NONE = ""

class Scene:
	def __init__(self, level, display_on_screen: bool, screen = None):
		self._level = level
		self._display_on_screen = display_on_screen
		self._screen = screen

		self._create_scene()

	def _create_scene(self):
		self._create_moves()
		self._create_bricks(self._level)

		if self._display_on_screen:
			self._background = pygame.Surface(display_area_size)
			self._background.fill((0, 0, 0))	# black

	def _create_moves(self):
		display_area_rect = pygame.Rect((0, 0), display_area_size)

		self._group_move = pygame.sprite.RenderPlain()
		self._ball = gameobject.Ball((100, 100), \
			display_area_rect, self._group_move)
		self._platform = gameobject.Platform((75, 400), \
			display_area_rect, self._group_move)

		if self._display_on_screen:
			self._ball.create_surface()
			self._platform.create_surface()

	def _create_bricks(self, level: int):
		def get_coordinate(string):
			string = string.rstrip("\n").split(' ')
			return int(string[0]), int(string[1])

		self._group_brick = pygame.sprite.RenderPlain()
		self._brick_container = []

		dir_path = os.path.dirname(__file__)
		level_file_path = os.path.join(dir_path, "level_data/{0}.dat".format(level))
		with open(level_file_path, 'r') as input_file:
			offset_x, offset_y = get_coordinate(input_file.readline())
			for input_pos in input_file:
				pos_x, pos_y = get_coordinate(input_pos.rstrip("\n"))
				brick = gameobject.Brick((pos_x + offset_x, pos_y + offset_y), \
					self._group_brick)
				self._brick_container.append(brick)

				if self._display_on_screen:
					brick.create_surface()

	def reset(self):
		self._ball.reset()
		self._platform.reset()
		self._group_brick.empty()
		self._group_brick.add(*self._brick_container)

	def update(self, move_action: str) -> str:
		self._ball.move()
		self._platform.move(move_action)

		self._ball.check_hit_brick(self._group_brick)
		is_alive = self._ball.check_bouncing(self._platform)

		if len(self._group_brick) == 0:
			return GAME_PASS_MSG
		elif is_alive:
			return GAME_ALIVE_MSG
		else:
			return GAME_OVER_MSG

	def draw(self):
		if not self._display_on_screen:
			return

		self._screen.blit(self._background, (0, 0))
		self._group_move.draw(self._screen)
		self._group_brick.draw(self._screen)
