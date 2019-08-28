"""
The script that send the instruction according to the keyboard input
"""

import pygame
import pingpong.communication as comm
from pingpong.communication import (
	SceneInfo, GameInstruction, GameStatus, PlatformAction
)

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

	print("Invisible joystick is used. " \
		"Press Enter to start the {} ml process.".format(side))
	while wait_enter_key():
		pass

	comm.ml_ready()

	while True:
		scene_info = comm.get_scene_info()

		if scene_info.status == GameStatus.GAME_1P_WIN or \
		   scene_info.status == GameStatus.GAME_2P_WIN:
			comm.ml_ready()
			continue

		key_pressed_list = pygame.key.get_pressed()
		if key_pressed_list[pygame.K_LEFT]:
			comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
		elif key_pressed_list[pygame.K_RIGHT]:
			comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
		else:
			comm.send_instruction(scene_info.frame, PlatformAction.NONE)

		pygame.event.pump()
