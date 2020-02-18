import os.path

from mlgame.gamedev.recorder import RecorderHelper
from .gamecore import GameStatus

def get_record_handler(record_progress: bool, filename_prefix: str):
    """
    Get the record handler according to the `record_progress`

    If `record_progress` is True, it will return `RecorderHelper.record_handler()`
    for recording the game progress. Otherwise, it will return a dummy function which
    takes one argument.
    """
    if not record_progress:
        return lambda x: None

    recorder = RecorderHelper(get_log_dir(), \
        { "status": (GameStatus.GAME_1P_WIN, GameStatus.GAME_2P_WIN, GameStatus.GAME_DRAW) }, \
        filename_prefix)
    return recorder.record_handler

def get_log_dir():
    """
    Get the path of the log directory
    """
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
