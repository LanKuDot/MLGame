import pygame, time

from mlgame.gamedev.generic import quit_or_esc
from mlgame.communication import game as comm

from .arkanoid import Screen
from .gamecore import GameStatus, PlatformAction, Scene
from .record import get_record_handler

class Arkanoid:
    """
    The game for the machine learning mode
    """

    def __init__(self, fps: int, difficulty, level: int,
        record_progress: bool, one_shot_mode: bool):
        self._ml_name = "ml"
        self._ml_execute_time = 1.0 / fps
        self._frame_delayed = 0

        self._record_handler = get_record_handler(record_progress,
            "ml_" + str(difficulty) + "_" + str(level))
        self._one_shot_mode = one_shot_mode

        self._scene = Scene(difficulty, level)
        self._screen = Screen(Scene.area_rect.size, self._scene.draw_gameobjects)

    def game_loop(self):
        """
        The main loop of the game in machine learning mode

        The execution order in the loop:
        1. Send the scene information to the machine learning process.
        2. Wait for the key frame (During this period, machine learning process can
           process the information and generate the game instruction.)
        3. Check if there has a command to receive. If it has, receive the
           command. Otherwise, generate a dummy one.
        4. Pass the command received to the game and update the scene.
        5. If the game is over or passed, send the scene information containing the
           game status to the machine learning process, and reset the game.
        6. Back to 1.
        """
        comm.wait_ml_ready(self._ml_name)

        while not quit_or_esc():
            scene_info = self._scene.get_scene_info()
            command = self._make_ml_execute(scene_info)

            scene_info["command"] = command.value
            self._record_handler(scene_info)

            game_status = self._scene.update(command)

            self._screen.update(self._scene.catch_ball_times)

            if (game_status == GameStatus.GAME_OVER or
                game_status == GameStatus.GAME_PASS):
                scene_info = self._scene.get_scene_info()
                comm.send_to_ml(scene_info, self._ml_name)

                scene_info["command"] = None
                self._record_handler(scene_info)

                print(game_status.value)

                if self._one_shot_mode:
                    return

                self._scene.reset()
                self._frame_delayed = 0
                # Wait for ml process doing resetting jobs
                comm.wait_ml_ready(self._ml_name)

    def _make_ml_execute(self, scene_info):
        """
        Send the scene_info to the ml process and wait for the instruction
        """
        comm.send_to_ml(scene_info, self._ml_name)
        time.sleep(self._ml_execute_time)
        game_cmd = self._process_cmd(comm.recv_from_ml(self._ml_name))

        if (game_cmd["frame"] != -1 and
            scene_info["frame"] - game_cmd["frame"] > self._frame_delayed):
            self._frame_delayed = scene_info["frame"] - game_cmd["frame"]
            print("Delayed {} frame(s)".format(self._frame_delayed))

        return game_cmd["command"]

    def _process_cmd(self, cmd_received):
        """
        Process the command received and return the processed command
        """
        error_msg = "Received invalid command: %(reason)s"
        cmd_processed = {"frame": -1, "command": PlatformAction.NONE}

        # If it doesn't receive the command from the client, return the default one.
        if not cmd_received:
            return cmd_processed

        # Type checking and value checking
        try:
            if not isinstance(cmd_received, dict):
                raise TypeError("the game command", "dict")
            if not isinstance(cmd_received["frame"], int):
                raise TypeError("'frame'", "int")
            if not isinstance(cmd_received["command"], str):
                raise TypeError("'command'", "str")

            cmd_processed["frame"] = cmd_received["frame"]
            cmd_processed["command"] = PlatformAction(cmd_received["command"])
        except KeyError as e:
            print(error_msg % {"reason": "Missing {}".format(e)})
        except TypeError as e:
            print(error_msg % {"reason":
                "Wrong type of {}. Should be '{}'.".format(*e.args)})
        except ValueError as e:
            print(error_msg % {"reason": str(e)})

        return cmd_processed
