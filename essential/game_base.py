import abc
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
	def _generate_next_value_(name, start, count, last_values):
		# Use the name of the enum as the enum value
		# when use auto() to set the enum value.
		return name

	def __eq__(self, other):
		if isinstance(other, StringEnum):
			return super().__eq__(other)
		elif isinstance(other, str):
			return self.value == other

		return False

	def __ne__(self, other):
		return not self.__eq__(other)
