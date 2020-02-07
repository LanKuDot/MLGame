import pygame
import time
import os.path

from mlgame.gamedev.generic import quit_or_esc
from mlgame.communication import game as comm
from mlgame.communication.game import CommandReceiver

from . import gamecore
from .pingpong import Screen
from .gamecore import GameStatus, PlatformAction, Scene
from .record import get_record_handler
from ..communication import GameCommand

class PingPong:
    """
    The game core for the machine learning mode
    """
    def __init__(self, fps: int, game_over_score: int, record_progress):
        """
        Constructor

        @param fps The fps of the game
        @param game_over_score The game will stop when either side reaches this score
        @param record_progress Whether to record the game process or not
        """
        self._ml_1P = "ml_1P"
        self._ml_2P = "ml_2P"
        self._ml_execute_time = 1.0 / fps
        self._frame_delayed = [0, 0]    # 1P, 2P
        self._score = [0, 0]    # 1P, 2P
        self._game_over_score = game_over_score
        self._cmd_receiver = CommandReceiver( \
            GameCommand, {
                "command": PlatformAction
            }, GameCommand(-1, PlatformAction.NONE))

        self._record_handler = get_record_handler(record_progress, "ml")

        self._scene = Scene()
        self._screen = Screen(Scene.area_rect.size, self._scene.draw_gameobjects)

    def game_loop(self):
        """
        The main loop of the game execution
        """
        comm.wait_all_ml_ready()

        while not quit_or_esc():
            scene_info = self._scene.get_scene_info()

            # Send the scene info to the ml processes and wait for commands
            command_1P, command_2P = self._make_ml_execute(scene_info)

            scene_info.command_1P = command_1P
            scene_info.command_2P = command_2P
            self._record_handler(scene_info)

            # Update the scene
            game_status = self._scene.update(command_1P, command_2P)

            self._screen.update(self._score, self._scene._ball.speed)

            # If either of two sides wins, reset the scene and wait for ml processes
            # getting ready for the next round
            if game_status == GameStatus.GAME_1P_WIN or \
               game_status == GameStatus.GAME_2P_WIN:
                scene_info = self._scene.get_scene_info()
                self._record_handler(scene_info)
                comm.send_to_all_ml(scene_info)

                print("Frame: {}, Status: {}" \
                    .format(scene_info.frame, game_status.value))

                if self._game_over(game_status):
                    break

                self._scene.reset()
                self._frame_delayed = [0, 0]
                # Wait for ml processes doing their resetting jobs
                comm.wait_all_ml_ready()

        self._print_result()

    def _make_ml_execute(self, scene_info):
        """
        Send the scene_info to the ml process and wait for the instructions
        """
        comm.send_to_all_ml(scene_info)
        time.sleep(self._ml_execute_time)
        instructions = self._cmd_receiver.recv_all()

        self._check_frame_delayed(0, self._ml_1P, \
            scene_info.frame, instructions[self._ml_1P].frame)
        self._check_frame_delayed(1, self._ml_2P, \
            scene_info.frame, instructions[self._ml_2P].frame)

        return instructions[self._ml_1P].command, instructions[self._ml_2P].command

    def _check_frame_delayed(self, ml_index, ml_name, scene_frame, instruct_frame):
        """
        Update the `frame_delayed` if the received instruction frame is delayed
        """
        if instruct_frame != -1 and \
           scene_frame - instruct_frame > self._frame_delayed[ml_index]:
            self._frame_delayed[ml_index] = scene_frame - instruct_frame
            print("{} delayed {} frame(s)" \
                .format(ml_name, self._frame_delayed[ml_index]))

    def _game_over(self, status):
        if status == GameStatus.GAME_1P_WIN:
            self._score[0] += 1
        else:
            self._score[1] += 1

        return self._score[0] == self._game_over_score or \
            self._score[1] == self._game_over_score

    def _print_result(self):
        if self._score[0] > self._score[1]:
            win_side = "1P"
        elif self._score[0] == self._score[1]:
            win_side = "No one"
        else:
            win_side = "2P"

        print("{} wins! Final score: {}-{}".format(win_side, *self._score))
