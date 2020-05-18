import importlib
import traceback

from multiprocessing import Process, Pipe
from threading import Thread
from queue import Queue
from .communication import CommunicationSet, CommunicationHandler
from .exceptions import (
    GameProcessError, MLProcessError,
)

class ProcessManager:
    """
    Create and manage the processes, and set up communication channels between them

    @var _game_proc_helper The helper object for the game process
    @var _ml_proc_helpers A list storing helper objects for all ml processes
    @var _ml_proces A list storing process objects running ml processes
    """

    def __init__(self):
        self._game_proc_helper = None
        self._ml_proc_helpers = []
        self._ml_procs = []

    def set_game_process(self, execution_cmd, game_cls):
        """
        Set the game process

        @param execution_cmd A `ExecutionCommand` object that contains execution config
        @param game_cls The class of the game to be executed
        """
        self._game_proc_helper = GameProcessHelper(execution_cmd, game_cls)

    def add_ml_process(self, target_module, name = "", args = (), kwargs = {}):
        """
        Add a ml process

        @param target_module The full name of the module
               to be executed in the ml process. The module must have `MLPlay` class.
        @param name The name of the ml process
               If it is not specified, it will be "ml_0", "ml_1", and so on.
        @param args The positional arguments to be passed to the `MLPlay.__init__()`
        @param kwargs The keyword arguments to be passed to the `MLPlay.__init__()`
        """
        if name == "":
            name = "ml_" + str(len(self._ml_proc_helpers))

        for helper in self._ml_proc_helpers:
            if name == helper.name:
                raise ValueError("The name '{}' has been used.".format(name))

        helper = MLProcessHelper(target_module, name, args, kwargs)
        self._ml_proc_helpers.append(helper)

    def start(self):
        """
        Start the processes

        The ml processes are spawned and started first, and then the main process executes
        the game process. After returning from the game process, the ml processes will be
        terminated.

        Note that there must be 1 game process and at least 1 ml process set
        before calling this function. Otherwise, the RuntimeError will be raised.
        """
        if self._game_proc_helper is None:
            raise RuntimeError("The game process is not set. Cannot start the ProcessManager")
        if len(self._ml_proc_helpers) == 0:
            raise RuntimeError("No ml process added. Cannot start the ProcessManager")

        self._create_pipes()
        self._start_ml_processes()
        returncode = self._start_game_process()

        self._terminate()

        return returncode

    def _create_pipes(self):
        """
        Create communication pipes for processes
        """
        # Create pipes for Game process <-> ml process
        for ml_proc_helper in self._ml_proc_helpers:
            recv_pipe_for_game, send_pipe_for_ml = Pipe(False)
            recv_pipe_for_ml, send_pipe_for_game = Pipe(False)

            self._game_proc_helper.add_comm_to_ml(ml_proc_helper.name,
                recv_pipe_for_game, send_pipe_for_game)
            ml_proc_helper.set_comm_to_game(
                recv_pipe_for_ml, send_pipe_for_ml)

    def _start_ml_processes(self):
        """
        Spawn and start all ml processes
        """
        for ml_proc_helper in self._ml_proc_helpers:
            process = Process(target = _ml_process_entry_point,
                name = ml_proc_helper.name, args = (ml_proc_helper,))
            process.start()

            self._ml_procs.append(process)

    def _start_game_process(self):
        """
        Start the game process
        """
        returncode = 0
        try:
            _game_process_entry_point(self._game_proc_helper)
        except (MLProcessError, GameProcessError) as e:
            print("Error: Exception occurred in '{}' process:".format(e.process_name))
            print(e.message)
            returncode = 2

        return returncode

    def _terminate(self):
        """
        Stop all spawned ml processes if it exists
        """
        for ml_process in self._ml_procs:
            ml_process.terminate()


class GameProcessHelper:
    """
    The helper class that helps build the game process

    Store the information for starting the game process and
    provide the helper functions to communicate with the ml processes.
    """
    name = "_game"

    def __init__(self, execution_cmd, game_cls):
        """
        Constructor

        @param execution_cmd A `ExecutionCommand` object that contains execution config
        @param game_cls The class of the game to be executed
        """
        self.execution_cmd = execution_cmd
        self.game_cls = game_cls
        self._comm_to_ml_set = CommunicationSet()

    def add_comm_to_ml(self, to_ml: str, recv_end, send_end):
        """
        Add communication objects for communicating with specified ml process

        @param to_ml The name of the target ml process
        @param recv_end The communication object for receiving objects from that ml process
        @param send_end The communication object for sending objects to that ml process
        """
        self._comm_to_ml_set.add_recv_end(to_ml, recv_end)
        self._comm_to_ml_set.add_send_end(to_ml, send_end)

    def get_ml_names(self):
        """
        Get the registered ml names for the communication
        """
        return self._comm_to_ml_set.get_send_end_names()

    def send_to_ml(self, obj, to_ml: str):
        """
        Send an object to the specified ml process

        @param obj The object to be sent
        @param to_ml The name of the ml process
        """
        self._comm_to_ml_set.send(obj, to_ml)

    def send_to_all_ml(self, obj):
        """
        Send an object to all ml processes

        @param obj The object to be sent
        """
        self._comm_to_ml_set.send_all(obj)

    def recv_from_ml(self, from_ml: str, to_wait: bool = False):
        """
        Receive an object from the specified ml process

        If it receives an exception from the ml process, it will raise MLProcessError.
        If this function is invoked in a `try...except...` block,
        raise the MLProcessError outside the starting point of the game process for
        the ProcessManager to stop all processes.

        @param from_ml The name of the ml process
        @param to_wait Whether to wait the object send from the ml process
        @return The received object
        """
        obj = self._comm_to_ml_set.recv(from_ml, to_wait)
        if isinstance(obj, MLProcessError):
            raise obj

        return obj

    def recv_from_all_ml(self, to_wait: bool = False):
        """
        Receive objects from all ml processes

        @param to_wait Whether to wait the object send from the ml processes
        @return A dictionary. The key is the game of the ml process,
                the value is the received object from that process.
        """
        objs = {}
        # Receive the object one by one for the error raising
        # when receiving MLProcessError in `recv_from_ml`
        # instead of using `recv_all` in `CommunicationSet`
        for target_ml in self._comm_to_ml_set.get_recv_end_names():
            objs[target_ml] = self.recv_from_ml(target_ml, to_wait)

        return objs

class MLProcessHelper:
    """
    The helper class that helps build ml process

    It is similar to the GameProcessHelper but for the ml process
    """

    def __init__(self, target_module, name, args = (), kwargs = {}):
        """
        Constructor

        @param target_module The full name of the module to be executed in the process.
               The module must have `ml_loop` function.
        @param name The name of the ml process
        @param args The positional arguments to be passed to the `ml_loop`
        @param kwargs The keyword arguments to be passed to the `ml_loop`
        """
        self.target_module = target_module
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self._comm_to_game = CommunicationHandler()

    def set_comm_to_game(self, recv_end, send_end):
        """
        Set communication objects for communicating with game process

        @param recv_end The communication object for receiving objects from game process
        @param send_end The communication object for sending objects to game process
        """
        self._comm_to_game.set_recv_end(recv_end)
        self._comm_to_game.set_send_end(send_end)

    def start_recv_obj_thread(self):
        """
        Start a thread to keep receiving objects from the game
        """
        self._obj_queue = Queue(15)

        thread = Thread(target = self._keep_recv_obj_from_game)
        thread.start()

    def _keep_recv_obj_from_game(self):
        """
        Keep receiving object from the game and put it in the queue

        If the queue is full, the received object will be dropped.
        """
        while True:
            if self._obj_queue.full():
                self._obj_queue.get()
                print("Warning: The object queue for the process '{}' is full. "
                    "Drop the oldest object."
                    .format(self.name))

            self._obj_queue.put(self._comm_to_game.recv())

    def recv_from_game(self):
        """
        Receive an object from the game process

        @return The received object
        """
        return self._obj_queue.get()

    def send_to_game(self, obj):
        """
        Send an object to the game process

        @param obj An object to be sent
        """
        self._comm_to_game.send(obj)

    def send_exception(self, exception: MLProcessError):
        """
        Send an exception to the game process
        """
        self._comm_to_game.send(exception)


def _game_process_entry_point(helper: GameProcessHelper):
    """
    The real entry point of the game process
    """
    from .loops import GameMLModeExecutor

    executor = GameMLModeExecutor(helper)
    executor.start()

def _ml_process_entry_point(helper: MLProcessHelper):
    """
    The real entry point of the ml process
    """
    from .loops import MLExecutor

    executor = MLExecutor(helper)
    executor.start()
