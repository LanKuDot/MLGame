import pygame, time

from mlgame.gamedev.generic import quit_or_esc
from mlgame.gamedev.recorder import get_record_handler
from mlgame.communication import game as comm
from mlgame.communication.game import CommandReceiver

from .gamecore import GameStatus, PlatformAction, Scene
from ..communication import GameCommand
from ..main import get_log_dir

class Arkanoid:
    """
    The game for the machine learning mode
    """

    def __init__(self, fps: int, level: int, \
        record_progress: bool, one_shot_mode: bool):
        self._ml_name = "ml"
        self._ml_execute_time = 1.0 / fps
        self._frame_delayed = 0
        self._cmd_receiver = CommandReceiver( \
            GameCommand, {
                "command": PlatformAction
            }, GameCommand(-1, PlatformAction.NONE))

        self._record_handler = get_record_handler(record_progress, { \
                "status": (GameStatus.GAME_OVER, GameStatus.GAME_PASS) \
            }, get_log_dir())
        self._one_shot_mode = one_shot_mode

        self._init_display()
        self._scene = Scene(level)

    def _init_display(self):
        pygame.display.init()
        pygame.display.set_caption("Arkanoid")
        self._screen = pygame.display.set_mode(Scene.area_rect.size)

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

            scene_info.command = command.value
            self._record_handler(scene_info)

            game_status = self._scene.update(command)

            self._draw_scene()

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

    def _draw_scene(self):
        """
        Draw the scene to the display
        """
        self._screen.fill((0, 0, 0))
        self._scene.draw_gameobjects(self._screen)
        pygame.display.flip()
