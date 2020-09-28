import importlib
import traceback

from multiprocessing import Process, Pipe
from .loops import GameMLModeExecutorProperty, MLExecutorProperty
from .exceptions import ProcessError

class ProcessManager:
    """
    Create and manage processes for executing the game and the ml clients

    @var _game_proc_helper The helper object for the game process
    @var _ml_proc_helpers A list storing helper objects for all ml processes
    @var _ml_proces A list storing process objects running ml processes
    """

    def __init__(
            self, game_executor_propty: GameMLModeExecutorProperty,
            ml_executor_propties: list):
        """
        Constructor

        @param game_executor_propty The property for the game executor
        @param ml_executor_proties A list of `MLExecutorProperty` for the ml executors
        """
        self._game_executor_propty = game_executor_propty
        self._ml_executor_propties = ml_executor_propties
        self._ml_procs = []

    def start(self):
        """
        Start the processes

        The ml processes are spawned and started first, and then the main process executes
        the game process. After returning from the game process, the ml processes will be
        terminated.

        Note that there must be 1 game process and at least 1 ml process set
        before calling this function. Otherwise, the RuntimeError will be raised.
        """
        if self._game_executor_propty is None:
            raise RuntimeError("The game process is not set. Cannot start the ProcessManager")
        if len(self._ml_executor_propties) == 0:
            raise RuntimeError("No ml process added. Cannot start the ProcessManager")

        self._create_pipes()
        self._start_ml_processes()

        returncode = 0
        try:
            self._start_game_process()
        except ProcessError as e:
            print("Error: Exception occurred in '{}' process:".format(e.process_name))
            print(e.message)
            returncode = -1

        self._terminate()

        return returncode

    def _create_pipes(self):
        """
        Create communication pipes for processes
        """
        # Create pipes for Game process <-> ml process
        for ml_executor_propty in self._ml_executor_propties:
            recv_pipe_for_game, send_pipe_for_ml = Pipe(False)
            recv_pipe_for_ml, send_pipe_for_game = Pipe(False)

            self._game_executor_propty.comm_manager.add_comm_to_ml(
                ml_executor_propty.name,
                recv_pipe_for_game, send_pipe_for_game)
            ml_executor_propty.comm_manager.set_comm_to_game(
                recv_pipe_for_ml, send_pipe_for_ml)

    def _start_ml_processes(self):
        """
        Spawn and start all ml processes
        """
        for propty in self._ml_executor_propties:
            process = Process(target = _ml_process_entry_point,
                name = propty.name, args = (propty,))
            process.start()

            self._ml_procs.append(process)

    def _start_game_process(self):
        """
        Start the game process
        """
        _game_process_entry_point(self._game_executor_propty)

    def _terminate(self):
        """
        Stop all spawned ml processes if it exists
        """
        for ml_process in self._ml_procs:
            # Send stop signal to all alive ml processes
            if ml_process.is_alive():
                self._game_executor_propty.comm_manager.send_to_ml(
                    None, ml_process.name)

def _game_process_entry_point(propty: GameMLModeExecutorProperty):
    """
    The real entry point of the game process
    """
    from .loops import GameMLModeExecutor

    executor = GameMLModeExecutor(propty)
    executor.start()

def _ml_process_entry_point(propty: MLExecutorProperty):
    """
    The real entry point of the ml process
    """
    from .loops import MLExecutor

    executor = MLExecutor(propty)
    executor.start()
