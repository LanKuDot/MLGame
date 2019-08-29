from .game.gamecore import GameStatus, PlatformAction

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
	@var command_2P The command for platform_2P in this frame. Similar to `command_1P`.
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
		self.command_1P = PlatformAction.NONE
		self.command_2P = PlatformAction.NONE

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
		# Check the type of the arguments
		if not isinstance(frame, int):
			raise TypeError("Invalid type of 'frame' for 'GameInstruction'." \
				" Type 'int' is needed, but '{}' is given." \
				.format(type(frame).__name__))
		if not isinstance(command, PlatformAction):
			raise TypeError("Invalid type of 'command' for 'GameInstruction'." \
				" Type 'PlatformAction' is needed, but '{}' is given." \
				.format(type(command).__name__))

		self.frame = frame
		self.command = command

	def __str__(self):
		return "# Frame {}\n# Command {}".format(self.frame, self.command)

from mlgame.communication import ml as comm

# ====== Helper functions ====== #
def get_scene_info() -> SceneInfo:
	return comm.recv_from_game()

def send_instruction(frame: int, command: PlatformAction):
	comm.send_to_game(GameInstruction(frame, command))

def ml_ready():
	comm.ml_ready()