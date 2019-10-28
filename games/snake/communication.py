from .game.gameobject import SnakeAction
from .game.gamecore import SceneInfo, GameStatus

class GameCommand:
    def __init__(self, frame, command):
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
        print("# Frame {}\n# Command {}".format(self.frame. self.command))

from mlgame.communication import ml as comm

def ml_ready():
    comm.ml_ready()

def get_scene_info():
    return comm.recv_from_game()

def send_command(frame, command):
    comm.send_to_game(GameCommand(frame, command))
