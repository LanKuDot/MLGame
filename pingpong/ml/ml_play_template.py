"""
The template of the script for the machine learning process in game pingpong
"""

import pingpong.communication as comm
from pingpong.communication import (
	SceneInfo, GameInstruction, GameStatus, PlatformAction
)

def ml_loop():
	comm.ml_ready()

	while True:
		scene_info = comm.get_scene_info()

		if scene_info.status == GameStatus.GAME_1P_WIN or \
		   scene_info.status == GameStatus.GAME_2P_WIN:
			comm.ml_ready()

		comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
