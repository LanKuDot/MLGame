import pygame

from .gamecore import GameStatus, PlatformAction, Scene, color_1P, color_2P

class PingPong:
    def __init__(self, difficulty, game_over_score: int):
        self._score = [0, 0]    # 1P, 2P
        self._game_over_score = game_over_score
        self._scene = Scene(difficulty)

        self._pygame_init()

    def _pygame_init(self):
        pygame.display.init()
        pygame.display.set_caption("PingPong")
        self._surface = pygame.display.set_mode(Scene.area_rect.size)

        pygame.font.init()
        self._font = pygame.font.Font(None, 22)
        self._font_pos_1P = (1, self._surface.get_height() - 21)
        self._font_pos_2P = (1, 4)
        self._font_pos_speed = (self._surface.get_width() - 120,
            self._surface.get_height() - 21)

    def update(self, cmd_list_1P, cmd_list_2P):
        command_1P = cmd_list_1P[0] if cmd_list_1P else PlatformAction.NONE
        command_2P = cmd_list_2P[0] if cmd_list_2P else PlatformAction.NONE

        game_status = self._scene.update(command_1P, command_2P)
        self._draw_screen()

        if game_status != GameStatus.GAME_ALIVE:
            print(game_status.value)
            if self._game_over(game_status):
                self._print_result()
                return "QUIT"

            return "RESET"

    def _draw_screen(self):
        """
        Draw the scene to the display
        """
        self._surface.fill((0, 0, 0))
        self._scene.draw_gameobjects(self._surface)

        font_surface_1P = self._font.render(
            "1P: {}".format(self._score[0]), True, color_1P)
        font_surface_2P = self._font.render(
            "2P: {}".format(self._score[1]), True, color_2P)
        font_surface_speed = self._font.render(
            "Speed: {}".format(self._scene._ball.speed), True, (255, 255, 255))
        self._surface.blit(font_surface_1P, self._font_pos_1P)
        self._surface.blit(font_surface_2P, self._font_pos_2P)
        self._surface.blit(font_surface_speed, self._font_pos_speed)

        pygame.display.flip()

    def _game_over(self, status):
        """
        Check if the game is over
        """
        if status == GameStatus.GAME_1P_WIN:
            self._score[0] += 1
        elif status == GameStatus.GAME_2P_WIN:
            self._score[1] += 1
        else:   # Draw game
            self._score[0] += 1
            self._score[1] += 1

        is_game_over = (self._score[0] == self._game_over_score or
            self._score[1] == self._game_over_score)

        return is_game_over

    def _print_result(self):
        """
        Print the result
        """
        if self._score[0] > self._score[1]:
            win_side = "1P"
        elif self._score[0] == self._score[1]:
            win_side = "No one"
        else:
            win_side = "2P"

        print("{} wins! Final score: {}-{}".format(win_side, *self._score))

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
