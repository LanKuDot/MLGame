import abc
from multiprocessing.connection import Connection

class GameABC(abc.ABC):
	@abc.abstractmethod
	def game_loop(self, fps: int, \
		instruct_pipe: Connection, pos_pipe: Connection, main_pipe: Connection):
		return NotImplemented
