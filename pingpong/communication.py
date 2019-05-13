from essential.game_base import StringEnum
from enum import auto

class GameStatus(StringEnum):
	GAME_1P_WIN = auto()
	GAME_2P_WIN = auto()
	GAME_ALIVE = auto()

class PlatformAction(StringEnum):
	READY = auto()
	NONE = auto()
	MOVE_LEFT = "LEFT"
	MOVE_RIGHT = "RIGHT"

class SceneInfo:
	"""
	The data structure for storing the information of the scene

	Note that SceneInfo won't take care of the delaying of command received.

	@var frame The frame number of the game
	@var status The status of the game. It will be the "value" (not "name")
	     of one of the member of the GameStatus.
	@var ball An (x, y) tuple. The position of the ball.
	@var ball_speed A positive integer. The speed of the ball.
	@var platform_1P An (x, y) tuple. The position of the platform of 1P
	@var platform_2P An (x, y) tuple. The position of the platform of 2P
	@var command_1P The command for platform_1P in this frame. It will be the "value"
	     (not "name") of one of the member of the PlatformAction.
	@var command_2P The command for plarform_2P in this frame. Similiar to `command_1P`.
	"""
	def __init__(self):
		# These fields will be filled before being sent to the ml process
		self.frame = None
		self.status = None
		self.ball = None
		self.ball_speed = None
		self.platform_1P = None
		self.platform_2P = None

		# These fields will be filled after receiving the instruction
		# from the ml process
		self.command_1P = "NONE"
		self.command_2P = "NONE"

	def __str__(self):
		output_str = "# Frame {}\n".format(self.frame)
		output_str += "# Status {}\n".format(self.status)
		output_str += "# Ball {} {}\n".format(*self.ball)
		output_str += "# Ball_speed {}\n".format(self.ball_speed)
		output_str += "# Platform_1P {} {}\n".format(*self.platform_1P)
		output_str += "# Platform_2P {} {}\n".format(*self.platform_2P)
		output_str += "# Command_1P {}\n".format(self.command_1P)
		output_str += "# Command_2P {}".format(self.command_2P)

		return output_str

class GameInstruction:
	"""
	The data structure for ml process to control the platform
	"""
	def __init__(self, frame: int, command: PlatformAction):
		"""
		Constructor

		@var frame The frame number which this GameInstruction is for
		@var command The command for controlling the platform. It will be one
		     of the PlatformAction.
		"""
		self.frame = frame
		self.command = command

	def __str__(self):
		return "# Frame {}\n# Command {}".format(self.frame, self.command)

# Communication pipes between ml process and game processes
# They are initialized before the ml process starts.
_scene_info_pipe = None
_instruct_pipe = None

# ====== Helper functions ====== #
def get_scene_info() -> SceneInfo:
	return _scene_info_pipe.recv()

def send_instruction(frame: int, command: PlatformAction):
	_instruct_pipe.send(GameInstruction(frame, command))

def ml_ready():
	send_instruction(0, PlatformAction.READY)