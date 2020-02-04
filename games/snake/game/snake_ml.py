"""
The game execution form the ml mode
"""

import pygame
import time

from mlgame.gamedev.generic import quit_or_esc
from mlgame.communication import game as comm
from mlgame.communication.game import CommandReceiver

from .gamecore import Scene, GameStatus
from .gameobject import SnakeAction
from .record import get_record_handler
from ..communication import GameCommand

class Snake:
    """
    The game execution manager
    """

    def __init__(self, fps, one_shot_mode, record_progress):
        self._init_pygame()

        self._scene = Scene()

        self._ml_name = "ml"
        self._ml_execution_time = 1 / fps
        self._frame_delayed = 0
        self._cmd_receiver = CommandReceiver( \
            GameCommand, {
                "command": SnakeAction,
            }, GameCommand(-1, SnakeAction.NONE))

        self._one_shot_mode = one_shot_mode
        self._record_handler = get_record_handler(record_progress, "ml")

    def _init_pygame(self):
        """
        Initialize the required pygame module
        """
        pygame.display.init()
        pygame.display.set_caption("Snake")
        self._screen = pygame.display.set_mode( \
            (Scene.area_rect.width, Scene.area_rect.height + 25))

        pygame.font.init()
        self._font = pygame.font.Font(None, 22)
        self._font_pos = (1, Scene.area_rect.width + 5)

    def game_loop(self):
        """
        The game execution loop
        """
        # Wait for the ml process
        comm.wait_ml_ready(self._ml_name)

        while not quit_or_esc():
            # Generate the scene information
            scene_info = self._scene.get_scene_info()

            # Send the scene information to the ml process
            # and wait the command sent from it
            command = self._make_ml_execute(scene_info)

            # Record the scene information
            scene_info.command = command
            self._record_handler(scene_info)

            # Update the scene
            game_status = self._scene.update(command)

            # If the game is over, reset the scene or
            # quit the game loop if one shot mode is set.
            if game_status == GameStatus.GAME_OVER:
                # Send the scene info with the game over status
                # and record that scene info
                scene_info = self._scene.get_scene_info()
                comm.send_to_ml(scene_info, self._ml_name)
                self._record_handler(scene_info)

                if self._one_shot_mode:
                    return

                self._scene.reset()
                self._frame_delayed = 0

                # Wait for the ml process for the next round
                comm.wait_ml_ready(self._ml_name)

            # Draw the scene to the display
            self._draw_scene()

    def _make_ml_execute(self, scene_info):
        """
        Send the scene info to the ml process and receive the command from it

        The method will wait the ml process to execute the command for a period
        which is decided by the `_ml_execution_time`.
        If the ml process can't send the command in time,
        the method will return a default command.
        """
        comm.send_to_ml(scene_info, self._ml_name)
        time.sleep(self._ml_execution_time)
        game_cmd = self._cmd_receiver.recv(self._ml_name)

        # Check and update the frame delayed
        if game_cmd.frame != -1 and \
           scene_info.frame - game_cmd.frame > self._frame_delayed:
            self._frame_delayed = scene_info.frame - game_cmd.frame

        return game_cmd.command

    def _draw_scene(self):
        """
        Draw the scene to the display
        """
        self._screen.fill((50, 50, 50))
        self._screen.fill((0, 0, 0), Scene.area_rect)
        self._scene.draw_gameobjects(self._screen)

        # Draw score
        font_surface = self._font.render( \
            "Score: {}, Frame delayed: {}".format(self._scene.score, self._frame_delayed), \
            True, (255, 255, 255))
        self._screen.blit(font_surface, self._font_pos)

        pygame.display.flip()
