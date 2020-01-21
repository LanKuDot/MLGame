from .game.gamecore import GameStatus, PlatformAction, SceneInfo

class GameCommand:
    """
    The data structure for controlling the game

    To control the game, the ml process should generate a GameInstruction and
    pass to the game process.

    @var frame The frame no. this GameInstruction for. It is recommended to set it
         as the SceneInfo.frame
    @var command The command for controlling the platform. It could only be one of
         `PlatformAction`.
    """

    def __init__(self, frame: int, command: PlatformAction):
        # Check the type of the arguments
        if not isinstance(frame, int):
            raise TypeError("Invalid type of 'frame' for 'GameCommand'." \
                " Type 'int' is needed, but '{}' is given." \
                .format(type(frame).__name__))
        if not isinstance(command, PlatformAction):
            raise TypeError("Invalid type of 'command' for 'GameCommand'." \
                " Type 'PlatformAction' is needed, but '{}' is given." \
                .format(type(command).__name__))

        self.frame = frame
        self.command = command

    def __str__(self):
        return "# Frame {}\n# Command {}".format(self.frame, self.command)

from mlgame.communication import ml as comm

# ====== Helper functions ====== #
def get_scene_info() -> SceneInfo:
    """
    Get the scene information from the game process
    """
    return comm.recv_from_game()

def send_instruction(frame: int, command: PlatformAction):
    """
    Send a game instruction to the game process

    @param frame The frame number for the corresponding scene information
    @param command The game command. It could only be the command defined
           in the class PlatformAction.
    """
    comm.send_to_game(GameCommand(frame, command))

def ml_ready():
    """
    Inform the game process that ml process is ready
    """
    comm.ml_ready()
