import pickle
import time

from pathlib import Path
from .execution_command import GameMode

RECORD_FORMAT_VERSION = 2

def get_recorder(execution_cmd, ml_names):
    """
    The helper function for generating a recorder object
    """
    if not execution_cmd.record_progress:
        return DummyRecorder()

    root_dir_path = Path(__file__).parent.parent
    log_dir_path = root_dir_path.joinpath(
        "games", execution_cmd.game_name, "log")

    game_params_str = [str(p) for p in execution_cmd.game_params]
    filename_prefix = (
        "manual" if execution_cmd.game_mode == GameMode.MANUAL else "ml")
    if game_params_str:
        filename_prefix += "_" + "_".join(game_params_str)

    return Recorder(ml_names, log_dir_path, filename_prefix)

class Recorder:
    """
    Record the scene information and the game command to the file
    """
    def __init__(
            self, ml_names: list, saving_directory: Path,
            filename_prefix: str = ""):
        """
        Constructor

        @param ml_names A list containing the name of all ml clients
        @param saving_directory Specify the directory for saving files
        @param filename_prefix Specify the prefix of the filename to be generated.
               The filename will be "<prefix>_YYYY-MM-DD_hh-mm-ss.pickle".
        """
        self._saving_directory = saving_directory
        if not self._saving_directory.exists():
            self._saving_directory.mkdir()

        if not isinstance(filename_prefix, str):
            raise TypeError("'filename_prefix' should be the type of 'str'")
        self._filename_prefix = filename_prefix

        # Create storing slots for each ml client
        game_progress = {
            "record_format_version": RECORD_FORMAT_VERSION
        }
        for name in ml_names:
            game_progress[name] = {
                "scene_info": [],
                "command": []
            }
        self._game_progress = game_progress
        self._ml_names = ml_names

    def record(self, scene_info_dict: dict, cmd_dict: dict):
        """
        Record the scene information and the command

        The received scene information will be stored in a list.

        @param scene_info_dict A dict storing the scene information for each client
        @param cmd_dict A dict storing the command received from each client
        """
        for name in self._ml_names:
            target_slot = self._game_progress[name]
            scene_info = scene_info_dict.get(name, None)
            if scene_info:
                target_slot["scene_info"].append(scene_info)
                target_slot["command"].append(cmd_dict.get(name, None))

    def flush_to_file(self):
        """
        Flush the stored objects to the file
        """
        filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".pickle"

        if self._filename_prefix:
            filename = self._filename_prefix + "_" + filename

        filepath = self._saving_directory.joinpath(filename)
        with open(filepath, "wb") as f:
            pickle.dump(self._game_progress, f)

        for name in self._ml_names:
            target_slot = self._game_progress[name]
            target_slot["scene_info"].clear()
            target_slot["command"].clear()

class DummyRecorder:
    """
    The recorder that only proivdes the API of `Recorder` but do nothing
    """
    def __init__(self):
        pass

    def record(self, scene_info, commands):
        pass

    def flush_to_file(self):
        pass
