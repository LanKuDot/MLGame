"""
The API for the player to write the program to play the game
"""

# Import the required class defined in the game
from .game.gameobject import SnakeAction
from .game.gamecore import SceneInfo, GameStatus

class GameCommand:
    """
    The game command sent from the ml process to play the game

    @var frame The number of frame that this command is for
    @var command The command for this frame
    """

    def __init__(self, frame, command):
        # Check if the type of the `frame` and `command` is valid or not
        if not isinstance(frame, int):
            raise TypeError("Invalid type of 'frame' for 'GameCommand'. " \
                "Type 'int' is needed, but '{}' is given." \
                .format(type(frame).__name__))
        if not isinstance(command, SnakeAction):
            raise TypeError("Invalid type of 'command' for 'GameCommand'. " \
                "Type 'SnakeAction' is needed, but '{}' is given." \
                .format(type(command).__name__))

        self.frame = frame
        self.command = command

    def __str__(self):
        print("# Frame {}\n# Command {}".format(self.frame, self.command))

from mlgame.communication import ml as comm

def ml_ready():
    """
    Inform the game process that the ml process is ready
    """
    comm.ml_ready()

def get_scene_info():
    """
    Get the scene info sent from the game process
    """
    return comm.recv_from_game()

def send_command(frame, command):
    """
    Send the game command to the game process
    """
    comm.send_to_game(GameCommand(frame, command))
