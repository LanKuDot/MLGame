from multiprocessing import Process, Pipe
from .communication import CommunicationSet

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
		self._game_process = None
		self._ml_processes = []

		self._is_running = False

	@property
	def is_running(self):
		return self._is_running

	def set_game_process(self, target, name = "", args = (), kwargs = {}):
		if name == "":
			name = "game"

		self._game_process = ProcessData(target, name, args, kwargs)

	def add_ml_process(self, target, name = "", args = (), kwargs = {}):
		if name == "":
			name = "ml_" + len(self._ml_processes)

		ml_process = ProcessData(target, name, args, kwargs)
		self._ml_processes.append(ml_process)

	def start(self):
		if self._game_process is None:
			raise RuntimeError("The game process is not set. Cannot start the ProcessManager")
		if len(self._ml_processes) == 0:
			raise RuntimeError("No ml process added. Cannot start the ProcessManager")

		if self._is_running:
			return

		self._is_running = True

		self._create_pipes()
		self._start_ml_processes()
		self._start_game_process()

	def _create_pipes(self):
		for ml_process in self._ml_processes:
			# Create pipe for Game process -> ML process
			recv_pipe, send_pipe = Pipe(False)
			self._game_process._comm_set.send_end[ml_process._name] = send_pipe
			ml_process._comm_set.recv_end[self._game_process._name] = recv_pipe

			# Create pipe for ML process -> Game process
			recv_pipe, send_pipe = Pipe(False)
			ml_process._comm_set.send_end[self._game_process._name] = send_pipe
			self._game_process._comm_set.recv_end[ml_process._name] = recv_pipe

	def _start_ml_processes(self):
		for ml_process in self._ml_processes:
			ml_process._process_obj = Process( \
				None, ml_process._target, ml_process._name, \
				ml_process._args, ml_process._kwargs)
			ml_process._process_obj.start()

	def _start_game_process(self):
		self._game_process._target(*self._game_process._args, **self._game_process._kwargs)

	def terminate(self):
		for ml_process in self._ml_processes:
			ml_process._process_obj.terminate()

		self._is_running = False
