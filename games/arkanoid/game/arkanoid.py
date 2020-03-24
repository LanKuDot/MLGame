import pygame

from mlgame.gamedev.generic import quit_or_esc, KeyCommandMap

from .gamecore import GameStatus, PlatformAction, Scene
from .record import get_record_handler

class Screen:
    """
    The class for drawing the scene to the screen
    """

    def __init__(self, size, func_draw_gameobjects):
        """
        Constructor

        @param size The (width, height) tuple to define the size of the screen
        @param func_draw_gameobject The function for drawing gameobjects to the screen.
               The function should have 1 argument for passing the `Surface` object.
        """
        pygame.display.init()
        pygame.display.set_caption("Arkanoid")
        self._surface = pygame.display.set_mode(size)
        self._func_draw_gameobject = func_draw_gameobjects

        pygame.font.init()
        self._font = pygame.font.Font(None, 22)
        self._font_pos = (1, self._surface.get_height() - 21)

    def update(self, catch_ball_times):
        """
        Draw the scene to the screen

        @param catch_ball_times The number of times of catching ball
        """
        self._surface.fill((0, 0, 0))
        self._func_draw_gameobject(self._surface)

        font_surface = self._font.render(
            "Catching ball: {}".format(catch_ball_times),
            True, (255, 255, 255))
        self._surface.blit(font_surface, self._font_pos)

        pygame.display.flip()

class Arkanoid:
    def __init__(self, fps: int, difficulty, level: int, record_progress, one_shot_mode):
        self._fps = fps
        self._clock = pygame.time.Clock()

        self._scene = Scene(difficulty, level)
        self._keyboard = KeyCommandMap({
                pygame.K_a:     PlatformAction.SERVE_TO_LEFT,
                pygame.K_d:     PlatformAction.SERVE_TO_RIGHT,
                pygame.K_LEFT:  PlatformAction.MOVE_LEFT,
                pygame.K_RIGHT: PlatformAction.MOVE_RIGHT,
            }, PlatformAction.NONE)

        self._record_handler = get_record_handler(record_progress,
            "manual_" + str(difficulty) + "_" + str(level))
        self._one_shot_mode = one_shot_mode

        self._screen = Screen(Scene.area_rect.size, self._scene.draw_gameobjects)

    def game_loop(self):
        while not quit_or_esc():
            command = self._keyboard.get_command()
            self._record_scene_info(command)
            game_status = self._scene.update(command)

            if (game_status == GameStatus.GAME_OVER or
                game_status == GameStatus.GAME_PASS):
                print(game_status.value)
                self._record_scene_info(None)

                if self._one_shot_mode:
                    return

                self._scene.reset()

            self._screen.update(self._scene.catch_ball_times)
            self._clock.tick(self._fps)

    def _record_scene_info(self, command):
        scene_info = self._scene.get_scene_info()
        if command:
            scene_info.command = command
        self._record_handler(scene_info)
