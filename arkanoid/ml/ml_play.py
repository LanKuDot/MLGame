"""The main script of the machine learning process
"""

from .. import communication as comm
from ..communication import SceneInfo, GameInstruction

def ml_loop():
	"""The main loop of the machine learning process

	This loop is run in a seperate process, and it communicates with the game process.
	The execution order should be:
	1. Receive the SceneInfo from the game process.
	2. If the received SceneInfo indicates that the game is passed or over,
		receive the SceneInfo again, because the game process is reset.
	3. Do the machine learning procedure and generate the GameInstruction.
	4. Send the GameInstruction to the game process.
	5. Back to 1.

	Note that the game process will wait until ml process sends a READY command,
	so remember to send a READY command before starting the loop.
	The game process won't wait for the ml process to generate the
	GameInstrcution. It is possible that the frame of the GameInstruction
	is behind of the current frame in the game process. Try to decrease the fps
	to avoid this situation.
	"""

	comm.ml_ready()

	while True:
		scene_info = comm.get_scene_info()
		if scene_info.status == SceneInfo.STATUS_GAME_OVER or \
			scene_info.status == SceneInfo.STATUS_GAME_PASS:
			scene_info = comm.get_scene_info()

		comm.send_instruction(scene_info.frame, GameInstruction.CMD_LEFT)
