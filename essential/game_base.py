import abc
import pygame
from multiprocessing.connection import Connection
from enum import Enum

class BasicSceneInfo:
	STATUS_GAME_ALIVE = "GAME_ALIVE"
	STATUS_GAME_PASS = "GAME_PASS"
	STATUS_GAME_OVER = "GAME_OVER"

	def __init__(self):
		self.frame = -1
		self.status = BasicSceneInfo.STATUS_GAME_ALIVE

	def __str__(self):
		return "# Frame {}\n# Status {}".format(self.frame, self.status)

class GameABC(abc.ABC):
	@abc.abstractmethod
	def game_loop(self, fps: int, \
		instruct_pipe: Connection, pos_pipe: Connection, main_pipe: Connection):
		return NotImplemented

class StringEnum(Enum):
	def __eq__(self, other):
		if isinstance(other, StringEnum):
			return super().__eq__(other)
		elif isinstance(other, str):
			return self.value == other

		return False

	def __ne__(self, other):
		return not self.__eq__(other)

class KeyCommandMap:
	"""
	Map the keys to the commands and return the mapped command when the key is pressed
	"""
	def __init__(self, command_map: dict, default_command = None):
		"""
		Constructor

		@param command_map A dict which maps the keys to the commands.
		       The key of the dict is the key-code defined in pygame, and
		       the value is the command that will be returned when the corresponding
		       key is pressed.
		@param default_command The command will be returned when there is no
		       registered key pressed.
		"""
		if not isinstance(command_map, dict):
			raise TypeError("The 'action_dict' should be a 'dict'.")

		self._command_map = command_map
		self._default_command = default_command

	def get_command(self):
		"""
		Check the pressed key and return the corresponding command

		If there is no registered key pressed, return the `default_command` instead.
		Note that only one command is returned at once, and the key checking order is
		the same as the ordering in `command_map` (Python 3.6+).
		"""
		key_pressed_list = pygame.key.get_pressed()
		for key, command in self._command_map.items():
			if key_pressed_list[key]:
				return command
		return self._default_command

def quit_or_esc() -> bool:
	"""
	Check if the quit event is triggered or the ESC key is pressed.
	"""
	for event in pygame.event.get():
		if event.type == pygame.QUIT or \
		  (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			return True
	return False