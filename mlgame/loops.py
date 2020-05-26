"""
The loop executor for running games and ml client
"""

import importlib
import time
import traceback

from .communication import GameCommManager, MLCommManager
from .exceptions import GameProcessError, MLProcessError
from .gamedev.generic import quit_or_esc, KeyCommandMap
from .recorder import get_recorder

class GameManualModeExecutor:
    """
    The loop executor for the game process running in manual mode
    """
    def __init__(self, execution_cmd, game_cls, keyboard_maps):
        self._execution_cmd = execution_cmd
        self._game_cls = game_cls
        self._frame_interval = 1 / self._execution_cmd.fps
        self._keyboards = []
        for keymap in keyboard_maps:
            self._keyboards.append(KeyCommandMap(keymap))
        self._recorder = get_recorder(execution_cmd.game_name,
            execution_cmd.game_params, execution_cmd.game_mode,
            execution_cmd.record_progress)

    def start(self):
        """
        Start the loop for running the game
        """
        self._loop()

    def _loop(self):
        """
        The main loop for running the game
        """
        game = self._game_cls(*self._execution_cmd.game_params)

        while not quit_or_esc():
            scene_info = game.get_player_scene_info()
            time.sleep(self._frame_interval)
            commands = [keyboard.get_pressed_commands() for keyboard in self._keyboards]
            self._recorder.record(scene_info, commands)

            result = game.update(*commands)

            if result == "RESET" or result == "QUIT":
                scene_info = game.get_player_scene_info()
                self._recorder.record(scene_info,
                    [[] for _ in range(len(self._keyboards))])
                self._recorder.flush_to_file()

                if self._execution_cmd.one_shot_mode or result == "QUIT":
                    break

                game.reset()

class GameMLModeExecutorProperty:
    """
    The data class that helps build `GameMLModeExecutor`
    """
    def __init__(self, proc_name, execution_cmd, game_cls):
        """
        Constructor

        @param proc_name The name of the process
        @param execution_cmd A `ExecutionCommand` object that contains execution config
        @param game_cls The class of the game to be executed
        """
        self.proc_name = proc_name
        self.execution_cmd = execution_cmd
        self.game_cls = game_cls
        self.comm_manager = GameCommManager()

    def add_comm_to_ml(self, ml_name, recv_end, send_end):
        """
        Add communication objects for communicating with specified ml process

        @param ml_name The name of the target ml process
        @param recv_end The communication object for receiving objects from that ml process
        @param send_end The communication object for sending objects to that ml process
        """
        self.comm_manager.add_comm_to_ml(ml_name, recv_end, send_end)

class GameMLModeExecutor:
    """
    The loop executor for the game process running in ml mode
    """
    def __init__(self, propty: GameMLModeExecutorProperty):
        self._proc_name = propty.proc_name
        self._execution_cmd = propty.execution_cmd
        self._game_cls = propty.game_cls
        self._comm_manager = propty.comm_manager

        self._ml_names = self._comm_manager.get_ml_names()
        self._ml_execution_time = 1 / self._execution_cmd.fps
        self._ml_delayed_frames = {}
        for name in self._ml_names:
            self._ml_delayed_frames[name] = 0
        self._recorder = get_recorder(self._execution_cmd.game_name,
            self._execution_cmd.game_params, self._execution_cmd.game_mode,
            self._execution_cmd.record_progress)
        self._frame_count = 0

    def start(self):
        """
        Start the loop for the game process
        """
        try:
            self._loop()
        except MLProcessError:
            # This exception wil be raised when invoking `GameCommManager.recv_from_ml()`
            # and receive `MLProcessError` object from it
            raise
        except Exception:
            raise GameProcessError(self._proc_name, traceback.format_exc())

    def _loop(self):
        """
        The loop for sending scene information to the ml process, recevied the command
        sent from the ml process, and pass command to the game for execution.
        """
        game = self._game_cls(*self._execution_cmd.game_params)

        self._wait_all_ml_ready()
        while not quit_or_esc():
            scene_info = game.get_player_scene_info()
            commands = self._make_ml_execute(scene_info)
            self._recorder.record(scene_info, commands)

            result = game.update(*commands)
            self._frame_count += 1

            # Do reset stuff
            if result == "RESET" or result == "QUIT":
                scene_info = game.get_player_scene_info()
                self._comm_manager.send_to_all_ml(scene_info)
                self._recorder.record(scene_info,
                    [[] for _ in range(len(self._ml_names))])
                self._recorder.flush_to_file()

                if self._execution_cmd.one_shot_mode or result == "QUIT":
                    break

                game.reset()
                self._frame_count = 0
                for name in self._ml_names:
                    self._ml_delayed_frames[name] = 0
                self._wait_all_ml_ready()

    def _wait_all_ml_ready(self):
        """
        Wait until receiving "READY" commands from all ml processes
        """
        # Wait the ready command one by one
        for ml_name in self._ml_names:
            while self._comm_manager.recv_from_ml(ml_name) != "READY":
                pass

    def _make_ml_execute(self, scene_info):
        """
        Send the scene information to all ml processes and wait for commands
        """
        self._comm_manager.send_to_all_ml(scene_info)
        time.sleep(self._ml_execution_time)
        game_cmd_dict = self._comm_manager.recv_from_all_ml()

        commands = []
        for ml_name in self._ml_names:
            cmd_received = game_cmd_dict[ml_name]
            if cmd_received:
                self._check_delay(ml_name, scene_info["frame"], cmd_received["frame"])
                commands.append(cmd_received["command"])
            else:
                commands.append([])

        return commands

    def _check_delay(self, ml_name, scene_info_frame, cmd_frame):
        """
        Check if the timestamp of the received command is delayed
        """
        delayed_frame = scene_info_frame - cmd_frame
        if delayed_frame > self._ml_delayed_frames[ml_name]:
            self._ml_delayed_frames[ml_name] = delayed_frame
            print("The client '{}' delayed {} frame(s)".format(ml_name, delayed_frame))

class MLExecutorProperty:
    """
    The data class that helps build `MLExecutor`
    """
    def __init__(self, name, target_module, init_args = (), init_kwargs = {}):
        """
        Constructor

        @param target_module The full name of the module to be executed in the process.
               The module must have `ml_loop` function.
        @param name The name of the ml process
        @param init_args The positional arguments to be passed to the `MLPlay.__init__()`
        @param init_kwargs The keyword arguments to be passed to the `MLPlay.__init__()`
        """
        self.name = name
        self.target_module = target_module
        self.init_args = init_args
        self.init_kwargs = init_kwargs
        self.comm_manager = MLCommManager(name)

    def set_comm_to_game(self, recv_end, send_end):
        """
        Set the receiving end and sending end for communicating with game process
        """
        self.comm_manager.set_comm_to_game(recv_end, send_end)

class MLExecutor:
    """
    The loop executor for the machine learning process
    """

    def __init__(self, propty: MLExecutorProperty):
        self._name = propty.name
        self._target_module = propty.target_module
        self._init_args = propty.init_args
        self._init_kwargs = propty.init_kwargs
        self._comm_manager = propty.comm_manager
        self._frame_count = 0

    def start(self):
        """
        Start the loop for the machine learning process
        """
        self._comm_manager.start_recv_obj_thread()

        try:
            self._loop()
        except Exception as e:
            exception = MLProcessError(self._name, traceback.format_exc())
            self._comm_manager.send_to_game(exception)

    def _loop(self):
        """
        The loop for receiving scene information from the game, make ml class execute,
        and send the command back to the game.
        """
        ml_module = importlib.import_module(self._target_module, __package__)
        ml = ml_module.MLPlay(*self._init_args, **self._init_kwargs)

        self._ml_ready()
        while True:
            command = ml.update(self._comm_manager.recv_from_game())

            if command == "RESET":
                ml.reset()
                self._frame_count = 0
                self._ml_ready()
                continue

            if command:
                # Check if the command format is valid
                if not isinstance(command, list):
                    raise TypeError("The value of returned game command "
                        "should be a 'list'")

                self._comm_manager.send_to_game({
                    "frame": self._frame_count,
                    "command": command
                })
                self._frame_count += 1

    def _ml_ready(self):
        """
        Send a "READY" command to the game process
        """
        self._comm_manager.send_to_game("READY")
