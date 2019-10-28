import pygame
import time

from mlgame.gamedev.generic import quit_or_esc
from mlgame.gamedev.recorder import get_record_handler
from mlgame.communication import game as comm
from mlgame.communication.game import CommandReceiver

from .gamecore import Scene, GameStatus
from .gameobject import SnakeAction
from ..communication import GameCommand
from ..main import get_log_dir

class Snake:
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
        self._record_handler = get_record_handler(record_progress, {
            "status": (GameStatus.GAME_OVER, )
        }, get_log_dir())

    def _init_pygame(self):
        pygame.display.init()
        pygame.display.set_caption("Snake")
        self._screen = pygame.display.set_mode( \
            (Scene.area_size.width, Scene.area_size.height + 25))

        pygame.font.init()
        self._font = pygame.font.Font(None, 22)
        self._font_pos = (1, Scene.area_size.width + 5)

    def game_loop(self):
        comm.wait_ml_ready(self._ml_name)

        while not quit_or_esc():
            scene_info = self._scene.get_scene_info()

            command = self._make_ml_execute(scene_info)
            scene_info.command = command
            self._record_handler(scene_info)

            game_status = self._scene.update(command)

            if game_status == GameStatus.GAME_OVER:
                scene_info = self._scene.get_scene_info()
                comm.send_to_ml(scene_info, self._ml_name)
                self._record_handler(scene_info)

                if self._one_shot_mode:
                    return

                self._scene.reset()
                self._frame_delayed = 0

                comm.wait_ml_ready(self._ml_name)

            self._draw_scene()

    def _make_ml_execute(self, scene_info):
        comm.send_to_ml(scene_info, self._ml_name)
        time.sleep(self._ml_execution_time)
        game_cmd = self._cmd_receiver.recv(self._ml_name)

        if game_cmd.frame != -1 and \
           scene_info.frame - game_cmd.frame > self._frame_delayed:
            self._frame_delayed = scene_info.frame - game_cmd.frame

        return game_cmd.command

    def _draw_scene(self):
        """
        Draw the scene to the display
        """
        self._screen.fill((50, 50, 50))
        self._screen.fill((0, 0, 0), Scene.area_size)
        self._scene.draw_gameobjects(self._screen)

        # Draw score
        font_surface = self._font.render( \
            "Score: {}, Frame delayed: {}".format(self._scene.score, self._frame_delayed), \
            True, (255, 255, 255))
        self._screen.blit(font_surface, self._font_pos)

        pygame.display.flip()
