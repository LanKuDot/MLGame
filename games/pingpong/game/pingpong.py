import pygame

from mlgame.gamedev.generic import quit_or_esc, KeyCommandMap
from mlgame.gamedev.recorder import get_record_handler

from . import gamecore
from .gamecore import GameStatus, PlatformAction, Scene
from ..main import get_log_dir

class PingPong:
    def __init__(self, fps: int, game_over_score: int, record_progress: bool):
        self._init_pygame()

        self._fps = fps
        self._score = [0, 0]    # 1P, 2P
        self._game_over_score = game_over_score
        self._scene = Scene(True)
        self._keyboard_action_1P = KeyCommandMap({
                pygame.K_LEFT:  PlatformAction.MOVE_LEFT,
                pygame.K_RIGHT: PlatformAction.MOVE_RIGHT,
            }, PlatformAction.NONE)
        self._keyboard_action_2P = KeyCommandMap({
                pygame.K_a: PlatformAction.MOVE_LEFT,
                pygame.K_d: PlatformAction.MOVE_RIGHT,
            }, PlatformAction.NONE)

        self._record_handler = get_record_handler(record_progress, {
                "status": (GameStatus.GAME_1P_WIN, GameStatus.GAME_2P_WIN)
            }, get_log_dir())

    def _init_pygame(self):
        pygame.display.init()
        pygame.display.set_caption("PingPong")
        self._screen = pygame.display.set_mode(Scene.area_rect.size)
        self._clock = pygame.time.Clock()

        pygame.font.init()
        self._font = pygame.font.Font(None, 22)
        self._font_pos_1P = (1, self._screen.get_height() - 21)
        self._font_pos_2P = (1, 4)
        self._font_pos_speed = (self._screen.get_width() - 75, \
            self._screen.get_height() - 21)

    def game_loop(self):
        while not quit_or_esc():
            command_1P = self._keyboard_action_1P.get_command()
            command_2P = self._keyboard_action_2P.get_command()

            scene_info = self._scene.get_scene_info()
            scene_info.command_1P = command_1P.value
            scene_info.command_2P = command_2P.value
            self._record_handler(scene_info)

            game_status = self._scene.update(command_1P, command_2P)

            if game_status == GameStatus.GAME_1P_WIN or \
               game_status == GameStatus.GAME_2P_WIN:
                print(game_status.value)
                self._record_handler(self._scene.get_scene_info())
                if self._game_over(game_status):
                    break

                self._scene.reset()

            self._draw_scene()
            self._clock.tick(self._fps)

        if self._score[0] > self._score[1]:
            print("1P wins!")
        else:
            print("2P wins!")
        print("Final score: {}-{}".format(*self._score))

    def _draw_scene(self):
        self._screen.fill((0, 0, 0))
        self._scene.draw_gameobjects(self._screen)

        # Game status
        font_1P_surface = self._font.render( \
            "1P score: {}".format(self._score[0]), True, gamecore.color_1P)
        font_2P_surface = self._font.render( \
            "2P score: {}".format(self._score[1]), True, gamecore.color_2P)
        font_speed_surface = self._font.render( \
            "Speed: {}".format(abs(self._scene._ball._speed[0])), True, (255, 255, 255))
        self._screen.blit(font_1P_surface, self._font_pos_1P)
        self._screen.blit(font_2P_surface, self._font_pos_2P)
        self._screen.blit(font_speed_surface, self._font_pos_speed)

        pygame.display.flip()

    def _game_over(self, status):
        if status == GameStatus.GAME_1P_WIN:
            self._score[0] += 1
        else:
            self._score[1] += 1

        is_game_over = self._score[0] == self._game_over_score or \
            self._score[1] == self._game_over_score

        return is_game_over