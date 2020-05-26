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

    def update(self, command):
        """
        Update the game
        """
        command = (PlatformAction(command)
            if command in PlatformAction.__members__ else PlatformAction.NONE)

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

    def get_keyboard_command(self):
        """
        Get the command according to the pressed key command
        """
        key_pressed_list = pygame.key.get_pressed()

        if key_pressed_list[pygame.K_a]:     return "SERVE_TO_LEFT"
        if key_pressed_list[pygame.K_d]:     return "SERVE_TO_RIGHT"
        if key_pressed_list[pygame.K_LEFT]:  return "MOVE_LEFT"
        if key_pressed_list[pygame.K_RIGHT]: return "MOVE_RIGHT"

        return "NONE"

    def get_game_info(self):
        """
        Get the scene and object information for drawing on the web
        """
        return {
            "scene": {
                "size": [200, 500]
            },
            "game_object": [
                { "name": "ball", "size": [5, 5], "color": [44, 185, 214] },
                { "name": "platform", "size": [40, 5], "color": [66, 226, 126] },
                { "name": "brick", "size": [25, 10], "color": [244, 158, 66] },
                { "name": "hard_brick", "size": [25, 10], "color": [209, 31, 31] },
            ]
        }

    def get_game_progress(self):
        """
        Get the position of game objects for drawing on the web
        """
        scene_info = self._scene.get_scene_info()

        return {
            "game_object": {
                "ball": [scene_info["ball"]],
                "platform": [scene_info["platform"]],
                "brick": scene_info["bricks"],
                "hard_brick": scene_info["hard_bricks"],
            }
        }

    def get_game_result(self):
        """
        Get the game result for the web
        """
        scene_info = self._scene.get_scene_info()

        return {
            "frame_used": scene_info["frame"],
            "result": [scene_info["status"]],
            "brick_remain": len(scene_info["bricks"]),
        }
