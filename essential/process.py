import importlib
import traceback

from multiprocessing import Process, Pipe
from .communication import CommunicationSet
from .exception import ExceptionMessage, trim_callstack

class ProcessData:
	def __init__(self, target, name = "", args = (), kwargs = {}):
		self._process_obj = None
		self._target = target
		self._name = name
		self._args = args
		self._kwargs = kwargs
		self._comm_set = CommunicationSet()

class ProcessManager:
	def __init__(self):
		self._game_proc_data = None
		self._ml_proc_helpers = []
		self._ml_procs = []

	def set_game_process(self, target, args = (), kwargs = {}):
		self._game_proc_data = ProcessData(target, "game", args, kwargs)

	def add_ml_process(self, target_module, name = "", args = (), kwargs = {}):
		if name == "":
			name = "ml_" + len(self._ml_proc_helpers)

		for helper in self._ml_proc_helpers:
			if name == helper.name:
				raise ValueError("The name '{}' has been used.".format(name))

		helper = MLProcessHelper(target_module, name, args, kwargs)
		self._ml_proc_helpers.append(helper)

	def start(self):
		if self._game_proc_data is None:
			raise RuntimeError("The game process is not set. Cannot start the ProcessManager")
		if len(self._ml_proc_helpers) == 0:
			raise RuntimeError("No ml process added. Cannot start the ProcessManager")

		self._create_pipes()
		self._start_ml_processes()
		self._start_game_process()

	def _create_pipes(self):
		for ml_proc_helper in self._ml_proc_helpers:
			# Create pipe for Game process -> ML process
			recv_pipe, send_pipe = Pipe(False)
			self._game_proc_data._comm_set.send_end[ml_proc_helper.name] = send_pipe
			ml_proc_helper._comm_set.recv_end[self._game_proc_data._name] = recv_pipe

			# Create pipe for ML process -> Game process
			recv_pipe, send_pipe = Pipe(False)
			ml_proc_helper._comm_set.send_end[self._game_proc_data._name] = send_pipe
			self._game_proc_data._comm_set.recv_end[ml_proc_helper.name] = recv_pipe

	def _start_ml_processes(self):
		for ml_proc_helper in self._ml_proc_helpers:
			process = Process(target = _ml_process_entry_point, \
				name = ml_proc_helper.name, args = (ml_proc_helper,))
			process.start()

			self._ml_procs.append(process)

	def _start_game_process(self):
		proc_data = self._game_proc_data
		helper = GameProcessHelper(proc_data._name, proc_data._comm_set)
		_game_process_entry_point(helper, proc_data._target, proc_data._args, proc_data._kwargs)
		self._terminate()

	def _terminate(self):
		for ml_process in self._ml_procs:
			ml_process.terminate()

class BaseProcessHelper:
	def __init__(self, process_name, comm_set):
		self.process_name = process_name
		self._comm_set = comm_set

class GameProcessHelper(BaseProcessHelper):
	def send_scene_info(self, scene_info):
		for send_end in self._comm_set.send_end.values():
			send_end.send(scene_info)

	def recv_instructions(self):
		instructions = []
		for recv_end in self._comm_set.recv_end.values():
			instructions.append(recv_end.recv())

		return instructions

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

def _game_process_entry_point(helper: GameProcessHelper, \
	target_function, args = (), kwargs = {}):
	try:
		target_function(*args, **kwargs, helper = helper)
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