"""
The script that send the instruction according to the keyboard input
"""

import pygame
from mlgame.communication import ml as comm

def wait_enter_key():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return False
    return True

def init_pygame():
    pygame.display.init()
    pygame.display.set_mode((300, 100))
    pygame.display.set_caption("Invisible joystick")

def ml_loop(side: str):
    init_pygame()

    print("Invisible joystick is used. "
        "Press Enter to start the {} ml process.".format(side))
    while wait_enter_key():
        pass

    comm.ml_ready()

    while True:
        scene_info = comm.recv_from_game()

        if scene_info["status"] != "GAME_ALIVE":
            comm.ml_ready()
            continue

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

        comm.send_to_game({"frame": scene_info["frame"], "command": cmd})

        pygame.event.pump()
