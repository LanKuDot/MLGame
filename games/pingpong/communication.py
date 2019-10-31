from .game.gamecore import GameStatus, PlatformAction, SceneInfo

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