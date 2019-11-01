import pygame

from mlgame.gamedev.generic import quit_or_esc, KeyCommandMap
from mlgame.gamedev.recorder import get_record_handler

from .gamecore import GameStatus, PlatformAction, Scene
from ..main import get_log_dir

class Arkanoid:
    def __init__(self, fps: int, level: int, record_progress, one_shot_mode):
        self._init_pygame()

        self._fps = fps
        self._scene = Scene(level, True)
        self._keyboard = KeyCommandMap({
                pygame.K_LEFT:  PlatformAction.MOVE_LEFT,
                pygame.K_RIGHT: PlatformAction.MOVE_RIGHT,
            }, PlatformAction.NONE)

        self._record_handler = get_record_handler(record_progress, {
                "status": (GameStatus.GAME_OVER, GameStatus.GAME_PASS)
            }, get_log_dir())
        self._one_shot_mode = one_shot_mode

    def _init_pygame(self):
        pygame.display.init()
        pygame.display.set_caption("Arkanoid")
        self._screen = pygame.display.set_mode(Scene.area_rect.size)
        self._clock = pygame.time.Clock()

    def game_loop(self):
        while not quit_or_esc():
            self._record_handler(self._scene.get_scene_info())
            control_action = self._keyboard.get_command()
            game_status = self._scene.update(control_action)

            if game_status == GameStatus.GAME_OVER or \
               game_status == GameStatus.GAME_PASS:
                print(game_status.value)
                self._record_handler(self._scene.get_scene_info())

                if self._one_shot_mode:
                    return

                self._scene.reset()

            self._screen.fill((0, 0, 0))
            self._scene.draw_gameobjects(self._screen)
            pygame.display.flip()

            self._clock.tick(self._fps)
