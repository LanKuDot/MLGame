"""
The script that send the instruction according to the keyboard input
"""

import pygame

class MLPlay:
    def __init__(self, side):
        self._pygame_init()
        print("Invisible joystick is used for the {} side."
            .format(side))

    def _pygame_init(self):
        pygame.display.init()
        pygame.display.set_mode((300, 100))
        pygame.display.set_caption("Invisible joystick")

    def update(self, scene_info):
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"

        pygame.event.pump()
        key_pressed_list = pygame.key.get_pressed()
        if key_pressed_list[pygame.K_LEFT]:
            cmd = "MOVE_LEFT"
        elif key_pressed_list[pygame.K_RIGHT]:
            cmd = "MOVE_RIGHT"
        elif key_pressed_list[pygame.K_PERIOD]:
            cmd = "SERVE_TO_LEFT"
        elif key_pressed_list[pygame.K_SLASH]:
            cmd = "SERVE_TO_RIGHT"
        else:
            cmd = "NONE"

        return cmd

    def reset(self):
        pass
