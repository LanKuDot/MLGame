import abc
from multiprocessing.connection import Connection

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
