import pygame

from mlgame.gamedev.generic import quit_or_esc, KeyCommandMap

from . import gamecore
from .gamecore import GameStatus, PlatformAction, Scene
from .record import get_record_handler

class Screen:
    def __init__(self, size, func_draw_gameobjects):
        pygame.display.init()
        pygame.display.set_caption("PingPong")
        self._surface = pygame.display.set_mode(size)

        self._func_draw_gameobjects = func_draw_gameobjects

        pygame.font.init()
        self._font = pygame.font.Font(None, 22)
        self._font_pos_1P = (1, self._surface.get_height() - 21)
        self._font_pos_2P = (1, 4)
        self._font_pos_speed = (self._surface.get_width() - 75, \
            self._surface.get_height() - 21)

    def update(self, score, ball_speed):
        self._surface.fill((0, 0, 0))
        self._func_draw_gameobjects(self._surface)

        font_surface_1P = self._font.render( \
            "1P score: {}".format(score[0]), True, gamecore.color_1P)
        font_surface_2P = self._font.render( \
            "2P score: {}".format(score[1]), True, gamecore.color_2P)
        font_surface_speed = self._font.render( \
            "Speed: {}".format(ball_speed), True, (255, 255, 255))
        self._surface.blit(font_surface_1P, self._font_pos_1P)
        self._surface.blit(font_surface_2P, self._font_pos_2P)
        self._surface.blit(font_surface_speed, self._font_pos_speed)

        pygame.display.flip()

class PingPong:
    def __init__(self, fps: int, game_over_score: int, record_progress: bool):
        self._fps = fps
        self._clock = pygame.time.Clock()

        self._score = [0, 0]    # 1P, 2P
        self._game_over_score = game_over_score
        self._scene = Scene()
        self._keyboard_action_1P = KeyCommandMap({
                pygame.K_LEFT:  PlatformAction.MOVE_LEFT,
                pygame.K_RIGHT: PlatformAction.MOVE_RIGHT,
            }, PlatformAction.NONE)
        self._keyboard_action_2P = KeyCommandMap({
                pygame.K_a: PlatformAction.MOVE_LEFT,
                pygame.K_d: PlatformAction.MOVE_RIGHT,
            }, PlatformAction.NONE)

        self._record_handler = get_record_handler(record_progress, "manual")
        self._screen = Screen(Scene.area_rect.size, self._scene.draw_gameobjects)

    def game_loop(self):
        while not quit_or_esc():
            command_1P = self._keyboard_action_1P.get_command()
            command_2P = self._keyboard_action_2P.get_command()

            scene_info = self._scene.get_scene_info()
            scene_info.command_1P = command_1P
            scene_info.command_2P = command_2P
            self._record_handler(scene_info)

            game_status = self._scene.update(command_1P, command_2P)

            if game_status == GameStatus.GAME_1P_WIN or \
               game_status == GameStatus.GAME_2P_WIN:
                print(game_status.value)
                self._record_handler(self._scene.get_scene_info())
                if self._game_over(game_status):
                    break

                self._scene.reset()

            self._screen.update(self._score, self._scene._ball.speed)
            self._clock.tick(self._fps)

        self._print_result()

    def _game_over(self, status):
        if status == GameStatus.GAME_1P_WIN:
            self._score[0] += 1
        else:
            self._score[1] += 1

        is_game_over = self._score[0] == self._game_over_score or \
            self._score[1] == self._game_over_score

        return is_game_over

    def _print_result(self):
        if self._score[0] > self._score[1]:
            win_side = "1P"
        elif self._score[0] == self._score[1]:
            win_side = "No one"
        else:
            win_side = "2P"

        print("{} wins! Final score: {}-{}".format(win_side, *self._score))
