"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
import pingpong.communication as comm
from pingpong.communication import (
	SceneInfo, GameInstruction, GameStatus, PlatformAction
)

def ml_loop():
	# === Here is the execution order of the loop === #
	# 1. Put the initialization code here

	# 2. Inform the game process that ml process is ready
	comm.ml_ready()

	# 3. Start an endless loop
	while True:
		# 3.1. Receive the scene information sent from the game process
		scene_info = comm.get_scene_info()

		# 3.2. If either of two sides wins the game, do the updating or
		#      reseting stuff and inform the game process when the ml process
		#      is ready.
		if scene_info.status == GameStatus.GAME_1P_WIN or \
		   scene_info.status == GameStatus.GAME_2P_WIN:
			# Do something updating or reseting stuff

			# 3.2.1 Inform the game process that
			#       the ml process is ready for the next round
			comm.ml_ready()
			continue

		# 3.3 Put the code here to handle the scene information

		# 3.4 Send the instruction for this frame to the game process
		comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
