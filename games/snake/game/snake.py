import pygame

from .gamecore import Scene, GameStatus
from .gameobject import SnakeAction

class Snake:
    """
    The game execution manager
    """
    def __init__(self):
        self._scene = Scene()
        self._pygame_init()

    def _pygame_init(self):
        """
        Initialize the required pygame module
        """
        pygame.display.init()
        pygame.display.set_caption("Snake")
        self._screen = pygame.display.set_mode(
            (Scene.area_rect.width, Scene.area_rect.height + 25))

        pygame.font.init()
        self._font = pygame.font.Font(None, 22)
        self._font_pos = (1, Scene.area_rect.width + 5)

    def update(self, command):
        """
        Update the game
        """
        # Get the command from the cmd_list
        command = (SnakeAction(command)
            if command in SnakeAction.__members__ else SnakeAction.NONE)

        # Pass the command to the scene and get the status
        game_status = self._scene.update(command)

        # If the game is over, send the reset signal
        if game_status == GameStatus.GAME_OVER:
            print("Score: {}".format(self._scene.score))
            return "RESET"

        self._draw_screen()

    def _draw_screen(self):
        """
        Draw the scene to the display
        """
        self._screen.fill((50, 50, 50))
        self._screen.fill((0, 0, 0), Scene.area_rect)
        self._scene.draw_gameobjects(self._screen)

        # Draw score
        font_surface = self._font.render(
            "Score: {}".format(self._scene.score), True, (255, 255, 255))
        self._screen.blit(font_surface, self._font_pos)

        pygame.display.flip()

    def reset(self):
        """
        Reset the game

        This function is invoked when the executor receives the reset signal
        """
        self._scene.reset()

    def get_player_scene_info(self):
        """
        Get the scene information to be sent to the player
        """
        return self._scene.get_scene_info()

    def get_keyboard_command(self):
        """
        Get the command according to the pressed key
        """
        key_pressed_list = pygame.key.get_pressed()

        if key_pressed_list[pygame.K_UP]:     return "UP"
        if key_pressed_list[pygame.K_DOWN]:   return "DOWN"
        if key_pressed_list[pygame.K_LEFT]:   return "LEFT"
        if key_pressed_list[pygame.K_RIGHT]:  return "RIGHT"

        return "NONE"

    def get_game_info(self):
        return {
            "scene": {
                "size": [300, 300]
            },
            "game_object": [
                { "name": "snake_head", "size": [10, 10], "color": [31, 204, 42] },
                { "name": "snake_body", "size": [10, 10], "color": [255, 255, 255] },
                { "name": "food", "size": [10, 10], "color": [232, 54, 42] },
            ]
        }

    def get_game_progress(self):
        scene_info = self._scene.get_scene_info()

        return {
            "game_object": {
                "snake_head": [scene_info["snake_head"]],
                "snake_body": scene_info["snake_body"],
                "food": [scene_info["food"]]
            }
        }

    def get_game_result(self):
        scene_info = self._scene.get_scene_info()

        return {
            "frame_used": scene_info["frame"],
            "result": ["GAME_OVER"],
            "score": self._scene.score
        }
