from argparse import ArgumentParser, REMAINDER
from enum import Enum, auto
import os.path

from ._version import version
from .exceptions import ExecutionCommandError

def get_command_parser():
    """
    Generate an ArgumentParser for parse the arguments in the command line
    """
    usage_str = ("python %(prog)s [options] <game> [game_params]")
    description_str = ("A platform for applying machine learning algorithm "
        "to play pixel games. "
        "In default, the game runs in the machine learning mode. ")

    parser = ArgumentParser(usage = usage_str, description = description_str,
        add_help = False)

    parser.add_argument("game", type = str, nargs = "?",
        help = "the name of the game to be started")
    parser.add_argument("game_params", nargs = REMAINDER, default = None,
        help = "[optional] the additional settings for the game. "
        "Note that all arguments after <game> will be collected to 'game_params'.")

    group = parser.add_argument_group(title = "functional options")
    group.add_argument("--version", action = "version", version = version)
    group.add_argument("-h", "--help", action = "store_true",
        help = "show this help message and exit. "
        "If this flag is specified after the <game>, "
        "show the help message of the game instead.")
    group.add_argument("-l", "--list", action = "store_true", dest = "list_games",
        help = "list available games. If the game in the 'games' directory "
        "provides 'config.py' which can be loaded, it will be listed.")

    group = parser.add_argument_group(title = "game execution options",
        description = "Game execution options must be specified before <game> arguments.")
    group.add_argument("-f", "--fps", type = int, default = 30,
        help = "the updating frequency of the game process [default: %(default)s]")
    group.add_argument("-m", "--manual-mode", action = "store_true",
        help = "start the game in the manual mode instead of "
        "the machine learning mode [default: %(default)s]")
    group.add_argument("-r", "--record", action = "store_true", dest = "record_progress",
        help = "pickle the game progress (a list of SceneInfo) to the log file. "
        "One file for a round, and stored in '<game>/log/' directory. "
        "[default: %(default)s]")
    group.add_argument("-1", "--one-shot", action = "store_true", dest = "one_shot_mode",
        help = "quit the game when the game is passed or is over. "
        "Otherwise, the game will restart automatically. [default: %(default)s]")
    group.add_argument("-i", "--input-script", type = str, action = "append",
        default = None, metavar = "SCRIPT",
        help = "specify user script(s) for the machine learning mode. "
        "For multiple user scripts, use this flag multiple times. "
        "The script must have function `ml_loop()` and "
        "be put in the '<game>/ml/' directory. [default: %(default)s]")
    group.add_argument("--input-module", type = str, action = "append",
        default = None, metavar = "MODULE",
        help = "specify the absolute import path of user module(s) "
        "for the machine learning mode. For multiple user modules, "
        "use this flag multiple times. The module must have function "
        "`ml_loop()`. [default: %(default)s]")

    return parser

class GameMode(Enum):
    """
    The mode of the game
    """
    __slots__ = ()

    MANUAL = auto()
    ML = auto()

class ExecutionCommand:
    """
    The data class for storing the command of the game execution

    @var game_name The name of the game to be executed
    @var game_params A list of parameters for the game
    @var one_shot_mode Whether to execute the game for only once
    @var game_mode The mode of the game to be executed.
         It will be one of attributes of `GameMode`.
    @var record_progress Whether to record the game progress
    @var fps The FPS of the game
    @var input_modules A list of user modules for running the ML mode
    """

    def __init__(self, parsed_args):
        """
        Generate the game configuration from the parsed command line arguments
        """
        self.game_name = parsed_args.game
        self.game_params = parsed_args.game_params

        self.game_mode = GameMode.MANUAL if parsed_args.manual_mode else GameMode.ML
        self.one_shot_mode = parsed_args.one_shot_mode
        self.record_progress = parsed_args.record_progress

        self.fps = parsed_args.fps

        self.input_modules = []
        self.input_modules.extend(self._parse_ml_scripts(parsed_args.input_script))
        self.input_modules.extend(self._parse_ml_modules(parsed_args.input_module))
        if self.game_mode == GameMode.ML and len(self.input_modules) == 0:
            raise ExecutionCommandError("No script or module is specified. "
                "Cannot start the game in the machine learning mode.")

    def _parse_ml_scripts(self, input_scripts):
        """
        Check whether the provided input scripts are all existing or not

        If it passes, the name of scripts is converted to the absolute import path and
        return a list of them.
        Otherwise, raise the ExecutionCommandError.
        """
        if not input_scripts:
            return []

        top_dir_path = os.path.dirname(os.path.dirname(__file__))
        module_list = []

        for script_name in input_scripts:
            local_script_path = os.path.join("games", self.game_name, "ml", script_name)
            full_script_path = os.path.join(top_dir_path, local_script_path)

            if not os.path.exists(full_script_path):
                raise ExecutionCommandError(
                    "The script '{}' does not exist. "
                    "Cannot start the game in the machine learning mode."
                    .format(local_script_path))

            # If the assigned script is not a python file,
            # pack the crosslang client and the script into a tuple for futher handling.
            path_no_ext, extension = os.path.splitext(script_name)
            if extension != ".py":
                module_list.append(("mlgame.crosslang.ml_play", full_script_path))
            else:
                module_list.append("games.{}.ml.{}"
                    .format(self.game_name, script_name.split('.py')[0]))

        return module_list

    def _parse_ml_modules(self, input_modules):
        """
        Check whether the provided input modules are all existing or not

        This method only check the existing of the target file,
        not the directory which the target file is in is a package or not.
        """
        if not input_modules:
            return []

        top_dir_path = os.path.dirname(os.path.dirname(__file__))

        for module_path in input_modules:
            module_nodes = module_path.split('.')
            module_nodes[-1] += ".py"
            local_script_path = os.path.join(*module_nodes)
            full_script_path = os.path.join(top_dir_path, local_script_path)

            if not os.path.exists(full_script_path):
                raise ExecutionCommandError(
                    "The script '{}' does not exist. "
                    "Cannot start the game in the machine learning mode."
                    .format(local_script_path))

        return input_modules

    def __str__(self):
        return ("{" +
            "'game_name': '{}', ".format(self.game_name) +
            "'game_params': {}, ".format(self.game_params) +
            "'game_mode': {}, ".format(self.game_mode) +
            "'one_shot_mode': {}, ".format(self.one_shot_mode) +
            "'record_progress': {}, ".format(self.record_progress) +
            "'fps': {}, ".format(self.fps) +
            "'input_modules': {}".format(self.input_modules) +
            "}")
