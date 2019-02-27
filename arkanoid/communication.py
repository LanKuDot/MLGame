from essential.game_base import BasicSceneInfo

class SceneInfo(BasicSceneInfo):
	"""The data structure for the information of the scene

	Containing the frame no, the status, and the position of the gameobjects.
	Note that the position is the coordinate at the top-left corner of the gameobject.

	@var frame The frame number of the game. Used as the timestamp.
	@var status The status of the game. It will only be STATUS_GAME_ALIVE,
	     STATUS_GAME_PASS, or STATUS_GAME_OVER.
	@var ball A (x, y) tuple which is the position of the ball.
	@var platform A (x, y) tuple which is the position of the platform.
	@var bricks A list containing multiple (x, y) tuple which is
	     the position of the remaining bricks.
	"""

	def __init__(self):
		super().__init__()
		# These members will be filled in the game process.
		self.ball = None
		self.platform = None
		self.bricks = None

	def __str__(self):
		output_str = "# Frame {}\n".format(self.frame)
		output_str += "# Status {}\n".format(self.status)
		output_str += "# Ball 1\n"
		output_str += "{} {}\n".format(self.ball[0], self.ball[1])
		output_str += "# Platform 1\n"
		output_str += "{} {}\n".format(self.platform[0], self.platform[1])
		output_str += "# Brick {}\n".format(len(self.bricks))
		for brick in self.bricks:
			output_str += "{} {}\n".format(brick[0], brick[1])

		return output_str[:-1]

class GameInstruction:
	"""The data structure for controlling the game

	To control the game, the ml process should generate a GameInstruction and
	pass to the game process.

	@var frame The frame no. this GameInstruction for. It is recommended to set it
	     as the SceneInfo.frame
	@var command The command for controlling the platform. It could only be CMD_READY,
	     CMD_LEFT, CMD_RIGHT, CMD_NONE.
	"""

	CMD_READY = "READY"
	CMD_LEFT = "LEFT"
	CMD_RIGHT = "RIGHT"
	CMD_NONE = ""

	def __init__(self, frame: int, command: str):
		self.frame = frame
		self.command = command

	def __str__(self):
		return "# Frame {}\n# Command {}".format(self.frame, self.command)

# Communication pipes between ml and game processes
# They are initialized before the ml process starts.
_scene_info_pipe = None
_instruct_pipe = None

# ====== Helper functions ====== #
def get_scene_info() -> SceneInfo:
	"""Get the scene information from the game process
	"""
	return _scene_info_pipe.recv()

def send_instruction(frame: int, command: str):
	"""Send a game instruction to the game process

	@param frame The frame number for the corresponding scene information
	@param command The game command. It could only be the command defined
	       in the class GameInstruction.
	"""
	_instruct_pipe.send(GameInstruction(frame, command))

def ml_ready():
	"""Inform the game process that ml process is ready
	"""
	send_instruction(0, GameInstruction.CMD_READY)
