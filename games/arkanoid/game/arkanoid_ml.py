import pygame, time

from mlgame.gamedev.generic import quit_or_esc
from mlgame.communication import game as comm
from mlgame.communication.game import CommandReceiver

from .arkanoid import Screen
from .gamecore import GameStatus, PlatformAction, Scene
from .record import get_record_handler
from ..communication import GameCommand

class Arkanoid:
    """
    The game for the machine learning mode
    """

    def __init__(self, fps: int, difficulty, level: int, \
        record_progress: bool, one_shot_mode: bool):
        self._ml_name = "ml"
        self._ml_execute_time = 1.0 / fps
        self._frame_delayed = 0
        self._cmd_receiver = CommandReceiver( \
            GameCommand, {
                "command": PlatformAction
            }, GameCommand(-1, PlatformAction.NONE))

        self._record_handler = get_record_handler(record_progress, \
            "ml_" + str(difficulty) + "_" + str(level))
        self._one_shot_mode = one_shot_mode

        self._scene = Scene(difficulty, level)
        self._screen = Screen(Scene.area_rect.size, self._scene.draw_gameobjects)

    def game_loop(self):
        """
        The main loop of the game in machine learning mode

        The execution order in the loop:
        1. Send the SceneInfo to the machine learning process.
        2. Wait for the key frame (During this period, machine learning process can
           process the SceneInfo and generate the GameInstruction.)
        3. Check if there has a command to receive. If it has, receive the
           command. Otherwise, generate a dummy one.
        4. Pass the command received to the game and update the scene.
        5. If the game is over or passed, send the SceneInfo containing the
           game status to the machine learning process, and reset the game.
        6. Back to 1.
        """
        comm.wait_ml_ready(self._ml_name)

        while not quit_or_esc():
            scene_info = self._scene.get_scene_info()
            command = self._make_ml_execute(scene_info)

            scene_info.command = command
            self._record_handler(scene_info)

            game_status = self._scene.update(command)

            self._screen.update()

            if game_status == GameStatus.GAME_OVER or \
               game_status == GameStatus.GAME_PASS:
                scene_info = self._scene.get_scene_info()
                self._record_handler(scene_info)
                comm.send_to_ml(scene_info, self._ml_name)

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
        game_cmd = self._cmd_receiver.recv(self._ml_name)

        if game_cmd.frame != -1 and \
           scene_info.frame - game_cmd.frame > self._frame_delayed:
            self._frame_delayed = scene_info.frame - game_cmd.frame
            print("Delayed {} frame(s)".format(self._frame_delayed))

        return game_cmd.command
