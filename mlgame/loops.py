"""
The loop executor for running games and ml client
"""

import importlib
import time
import traceback

from .exceptions import GameProcessError, MLProcessError
from .gamedev.generic import quit_or_esc, KeyCommandMap
from .process import GameProcessHelper, MLProcessHelper
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

class GameMLModeExecutor:
    """
    The loop executor for the game process running in ml mode
    """
    def __init__(self, helper: GameProcessHelper):
        self._helper = helper
        self._execution_cmd = self._helper.execution_cmd
        self._game_cls = self._helper.game_cls
        self._ml_names = self._helper.get_ml_names()
        self._ml_execution_time = 1 / self._execution_cmd.fps
        self._ml_delayed_frames = {}
        for name in self._ml_names:
            self._ml_delayed_frames[name] = 0
        self._recorder = get_recorder(self._execution_cmd.game_name,
            self._execution_cmd.game_params, self._execution_cmd.game_mode,
            self._execution_cmd.record_progress)

    def start(self):
        """
        Start the loop for the game process
        """
        try:
            self._loop()
        except MLProcessError:
            # This exception wil be raised when invoking `recv_from_ml()` and
            # receive `MLProcessError` object from it
            raise
        except Exception:
            raise GameProcessError(self._helper.name, traceback.format_exc())

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

            # Do reset stuff
            if result == "RESET" or result == "QUIT":
                scene_info = game.get_player_scene_info()
                self._send_scene_info(scene_info)
                self._recorder.record(scene_info,
                    [[] for _ in range(len(self._ml_names))])
                self._recorder.flush_to_file()

                if self._execution_cmd.one_shot_mode or result == "QUIT":
                    break

                game.reset()
                for name in self._ml_names:
                    self._ml_delayed_frames[name] = 0
                self._wait_all_ml_ready()

    def _wait_all_ml_ready(self):
        """
        Wait until receiving "READY" commands from all ml processes
        """
        # Wait the ready command one by one
        for ml_name in self._ml_names:
            while self._helper.recv_from_ml(ml_name) != "READY":
                pass

    def _make_ml_execute(self, scene_info):
        """
        Send the scene information to all ml processes and wait for commands
        """
        self._send_scene_info(scene_info)
        time.sleep(self._ml_execution_time)
        game_cmd_dict = self._recv_game_commands()

        commands = []
        for ml_name in self._ml_names:
            cmd_received = game_cmd_dict[ml_name]
            if cmd_received:
                self._check_delay(ml_name, scene_info["frame"], cmd_received["frame"])
                commands.append(cmd_received["command"])
            else:
                commands.append([])

        return commands

    def _send_scene_info(self, scene_info):
        """
        Send the scene information to all ml processes
        """
        self._helper.send_to_all_ml(scene_info)

    def _recv_game_commands(self):
        """
        Receive game commands sent from all ml processes
        """
        return self._helper.recv_from_all_ml()

    def _check_delay(self, ml_name, scene_info_frame, cmd_frame):
        """
        Check if the timestamp of the received command is delayed
        """
        delayed_frame = scene_info_frame - cmd_frame
        if delayed_frame > self._ml_delayed_frames[ml_name]:
            self._ml_delayed_frames[ml_name] = delayed_frame
            print("The client '{}' delayed {} frame(s)".format(ml_name, delayed_frame))

class MLExecutor:
    """
    The loop executor for the machine learning process
    """

    def __init__(self, helper: MLProcessHelper):
        self._helper = helper

    def start(self):
        """
        Start the loop for the machine learning process
        """
        self._helper.start_recv_obj_thread()

        try:
            self._loop()
        except Exception as e:
            exception = MLProcessError(self._helper.name, traceback.format_exc())
            self._helper.send_exception(exception)

    def _loop(self):
        """
        The loop for receiving scene information from the game, make ml class execute,
        and send the command back to the game.
        """
        ml_module = importlib.import_module(self._helper.target_module, __package__)
        ml = ml_module.MLPlay(*self._helper.args, **self._helper.kwargs)

        self._ml_ready()
        while True:
            command = ml.update(self._helper.recv_from_game())

            if command == "RESET":
                ml.reset()
                self._ml_ready()
                continue

            if command:
                # Check if the command format is valid
                if not isinstance(command["frame"], int):
                    raise TypeError("The value of 'frame' in the returned game command "
                        "should be an 'int'")
                if not isinstance(command["command"], list):
                    raise TypeError("The value of 'command' in the returned game command "
                        "should be a 'list'")

                self._helper.send_to_game(command)

    def _ml_ready(self):
        """
        Send a "READY" command to the game process
        """
        self._helper.send_to_game("READY")
