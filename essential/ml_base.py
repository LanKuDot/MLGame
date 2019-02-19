import abc
from multiprocessing.connection import Connection

class MlABC(abc.ABC):
	@abc.abstractmethod
	def ml_loop(self, instruct_pipe: Connection, scene_info_pipe: Connection):
		return NotImplemented
