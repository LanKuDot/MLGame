import importlib
import traceback

from multiprocessing import Process, Pipe
from .communication import CommunicationSet
from .exception import ExceptionMessage, trim_callstack

class ProcessManager:
	def __init__(self):
		self._game_proc_helper = None
		self._ml_proc_helpers = []
		self._ml_procs = []

	def set_game_process(self, target, args = (), kwargs = {}):
		self._game_proc_helper = GameProcessHelper(target, args, kwargs)

	def add_ml_process(self, target_module, name = "", args = (), kwargs = {}):
		if name == "":
			name = "ml_" + len(self._ml_proc_helpers)

		for helper in self._ml_proc_helpers:
			if name == helper.name:
				raise ValueError("The name '{}' has been used.".format(name))

		helper = MLProcessHelper(target_module, name, args, kwargs)
		self._ml_proc_helpers.append(helper)

	def start(self):
		if self._game_proc_helper is None:
			raise RuntimeError("The game process is not set. Cannot start the ProcessManager")
		if len(self._ml_proc_helpers) == 0:
			raise RuntimeError("No ml process added. Cannot start the ProcessManager")

		self._create_pipes()
		self._start_ml_processes()
		self._start_game_process()
		self._terminate()

	def _create_pipes(self):
		for ml_proc_helper in self._ml_proc_helpers:
			# Create pipe for Game process -> ML process
			recv_pipe, send_pipe = Pipe(False)
			self._game_proc_helper._comm_set.send_end[ml_proc_helper.name] = send_pipe
			ml_proc_helper._comm_set.recv_end[self._game_proc_helper.name] = recv_pipe

			# Create pipe for ML process -> Game process
			recv_pipe, send_pipe = Pipe(False)
			ml_proc_helper._comm_set.send_end[self._game_proc_helper.name] = send_pipe
			self._game_proc_helper._comm_set.recv_end[ml_proc_helper.name] = recv_pipe

	def _start_ml_processes(self):
		for ml_proc_helper in self._ml_proc_helpers:
			process = Process(target = _ml_process_entry_point, \
				name = ml_proc_helper.name, args = (ml_proc_helper,))
			process.start()

			self._ml_procs.append(process)

	def _start_game_process(self):
		_game_process_entry_point(self._game_proc_helper)

	def _terminate(self):
		for ml_process in self._ml_procs:
			ml_process.terminate()

class GameProcessHelper:
	def __init__(self, target_function, args = (), kwargs = {}):
		self.target_function = target_function
		self.name = "game"
		self.args = args
		self.kwargs = kwargs
		self._comm_set = CommunicationSet()

	def send_to_ml(self, obj, to_ml: str):
		self._comm_set.send_end[to_ml].send(obj)

	def send_to_all_ml(self, obj):
		for send_end in self._comm_set.send_end.values():
			send_end.send(obj)

	def recv_from_ml(self, from_ml: str):
		return self._comm_set.recv_end[from_ml].recv()

	def recv_from_all_ml(self):
		objs = []
		for recv_end in self._comm_set.recv_end.values():
			objs.append(recv_end.recv())

		return objs

class MLProcessHelper:
	def __init__(self, target_module, name, args = (), kwargs = {}):
		self.target_module = target_module
		self.name = name
		self.args = args
		self.kwargs = kwargs
		self._comm_set = CommunicationSet()

	def recv_from_game(self):
		return self._comm_set.recv_end["game"].recv()

	def send_to_game(self, obj):
		self._comm_set.send_end["game"].send(obj)

	def send_exception(self, exc_msg: ExceptionMessage):
		self._comm_set.send_end["game"].send(exc_msg)

def _game_process_entry_point(helper: GameProcessHelper):
	try:
		from .handler import game
		game.send_to_all_ml.set_function(helper.send_to_all_ml)
		game.recv_from_all_ml.set_function(helper.recv_from_all_ml)

		helper.target_function(*helper.args, **helper.kwargs)
	except Exception as e:
		traceback.print_exc()

def _ml_process_entry_point(helper: MLProcessHelper):
	try:
		from .handler import ml
		ml.send_to_game_handler.set_function(helper.send_to_game)
		ml.recv_from_game_handler.set_function(helper.recv_from_game)

		ml_module = importlib.import_module(helper.target_module, __package__)
		ml_module.ml_loop(*helper.args, **helper.kwargs)
	except Exception as e:
		exc_msg = ExceptionMessage(helper.name, traceback.format_exc())
		helper.send_exception(exc_msg)