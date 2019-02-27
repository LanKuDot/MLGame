import pygame
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
		self._frame_count = 0
		self._game_status = GAME_ALIVE_MSG

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

		import os.path
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
		self._frame_count = 0
		self._game_status = GAME_ALIVE_MSG
		self._ball.reset()
		self._platform.reset()
		self._group_brick.empty()
		self._group_brick.add(*self._brick_container)

	def update(self, move_action: str) -> str:
		self._frame_count += 1

		self._ball.move()
		self._platform.move(move_action)

		self._ball.check_hit_brick(self._group_brick)
		is_alive = self._ball.check_bouncing(self._platform)

		if len(self._group_brick) == 0:
			self._game_status = GAME_PASS_MSG
		elif is_alive:
			self._game_status = GAME_ALIVE_MSG
		else:
			self._game_status = GAME_OVER_MSG

		return self._game_status

	def draw(self):
		if not self._display_on_screen:
			return

		self._screen.blit(self._background, (0, 0))
		self._group_move.draw(self._screen)
		self._group_brick.draw(self._screen)

	def fill_scene_info_obj(self, scene_info_obj):
		"""Fill the information of scene to the `scene_info_obj`

		This is a helper function. `scene_info_obj` has the basic member "frame" and
		"status", and it must have member "ball", "platform", and "bricks".
		The position of the objects will be assigned to these members accroding to
		the name. Here are the data:
		- scene_info_obj.ball: a (x, y) tuple, the position of the ball
		- scene_info_obj.platform: a (x, y) tuple, the position of the platform
		- scene_info_obj.bricks: a list whose elements are all (x, y) tuple,
		  the position of remaining bricks.

		@param scene The game scene containing the target gameobjects
		@param scene_info_obj The instance of some class to be filled with the
		       scene info.
		@return The filled `scene_info_obj`
		"""
		def get_pivot_point(rect):
			return (rect.x, rect.y)

		scene_info_obj.frame = self._frame_count
		scene_info_obj.status = self._game_status
		scene_info_obj.ball = get_pivot_point(self._ball.rect)
		scene_info_obj.platform = get_pivot_point(self._platform.rect)
		scene_info_obj.bricks = []
		for brick in self._group_brick:
			scene_info_obj.bricks.append(get_pivot_point(brick.rect))

		return scene_info_obj
