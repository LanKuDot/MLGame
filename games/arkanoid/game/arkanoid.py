import pygame

from .gamecore import GameStatus, PlatformAction, Scene

class Arkanoid:
    def __init__(self, difficulty, level: int):
        self._scene = Scene(difficulty, level)
        self._pygame_init()

    def _pygame_init(self):
        """
        Initial the pygame for drawing
        """
        pygame.display.init()
        pygame.display.set_caption("Arkanoid")
        self._surface = pygame.display.set_mode(Scene.area_rect.size)

        pygame.font.init()
        self._font = pygame.font.Font(None, 22)
        self._font_pos = (1, self._surface.get_height() - 21)

    def update(self, cmd_list):
        """
        Update the game
        """
        command = cmd_list[0] if cmd_list else PlatformAction.NONE
        game_status = self._scene.update(command)
        self._draw_screen()

        if (game_status == GameStatus.GAME_OVER or
            game_status == GameStatus.GAME_PASS):
            print(game_status.value)
            return "RESET"

    def _draw_screen(self):
        """
        Draw the scene to the display
        """
        self._surface.fill((0, 0, 0))
        self._scene.draw_gameobjects(self._surface)

        font_surface = self._font.render(
            "Catching ball: {}".format(self._scene.catch_ball_times),
            True, (255, 255, 255))
        self._surface.blit(font_surface, self._font_pos)

        pygame.display.flip()

    def reset(self):
        """
        Reset the game
        """
        self._scene.reset()

    def get_player_scene_info(self):
        """
        Get the scene information to be sent to the player
        """
        return self._scene.get_scene_info()
