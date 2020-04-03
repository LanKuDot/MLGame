"""
"""
import importlib
import sys

from .gameconfig import get_command_parser, GameMode, GameConfig
from .exception import GameConfigError
from .utils.argparser_generator import get_parser_from_dict

def execute():
    """
    Parse the execution command and execute the game
    """
    try:
        game_config = _get_game_config()
    except GameConfigError as e:
        print("Error:", e)
        sys.exit(1)

    try:
        _game_execution(game_config)
    except GameConfigError as e:
        print("Error:", e)
        sys.exit(1)

def _get_game_config() -> GameConfig:
    """
    Parse the game config specified from the command line and generate `GameConfig`

    @return A `GameConfig` object
    """
    # Parse the command line arguments
    cmd_parser = get_command_parser()
    parsed_args = cmd_parser.parse_args()

    # If "-h/--help" is specified, print help message and exit.
    if not parsed_args.game and parsed_args.help:
        cmd_parser.print_help()
        sys.exit(0)

    # Load the game defined parameters
    try:
        game_defined_config = importlib.import_module(
            "games.{}.config".format(parsed_args.game))
        game_defined_params = game_defined_config.GAME_PARAMS
    except ModuleNotFoundError:
        raise GameConfigError("Game '{}' dosen\'t provide 'config.py'"
            .format(parsed_args.game))
    except AttributeError:
        # The game doesn't define any game parameters, create a default one
        game_defined_params = {
            "()": {
                "prog": parsed_args.game,
                "game_usage": "%(prog)s"
            }
        }

    # Create game_param parser
    _preprocess_game_param_dict(game_defined_params)
    param_parser = get_parser_from_dict(game_defined_params)
    # If "-h/--help" and "<game>" are specified, print help and exit.
    if parsed_args.help:
        param_parser.print_help()
        sys.exit(0)

    # Replace the input game_params with the parsed one
    parsed_args.game_params = param_parser.parse_args(parsed_args.game_params)

    # Generate GameConfig
    try:
        config = GameConfig(parsed_args)
    except Exception as e:
        raise GameConfigError(str(e))

    return config

def _preprocess_game_param_dict(param_dict):
    """
    Preprocess the game defined `GAME_PARAMS`
    """
    # Append the command of MLGame to the `game_usage`
    # and set it to the `usage`
    if (param_dict.get("()") and
        param_dict["()"].get("game_usage")):
        game_usage = str(param_dict["()"].pop("game_usage"))
        param_dict["()"]["usage"] = (
            "python MLGame.py [options] " + game_usage + "\n" +
            "".ljust(24) + "[-i SCRIPTS/--input-module MODULES]")

def _game_execution(game_config: GameConfig):
    """
    Execute the game

    @param config The parsed game config
    """
    try:
        game_defined_config = importlib.import_module(
            "games.{}.config".format(game_config.game_name))
        game_defined_processes = game_defined_config.PROCESSES

        process_config = {
            GameMode.MANUAL: game_defined_processes["manual_mode"],
            GameMode.ML: game_defined_processes["ml_mode"]
        }.get(game_config.game_mode)
    except AttributeError:
        raise GameConfigError("'PROCESSES' is not defined in '{}'"
            .format(game_defined_config.__name__))
    except KeyError as e:
        raise GameConfigError("Cannot find {} in 'PROCESSES' in {}"
            .format(game_defined_config.__name__, e))
    # The exist of 'config.py' had been checked at '_parse_game_config',
    # so no need to catch ModuleNotFoundError.

    try:
        _preprocess_process_config(process_config, game_defined_config)
    except Exception as e:
        raise GameConfigError("Error occurred while preprocessing 'PROCESSES' in '{}': "
            "{}".format(game_defined_config.__name__, e))

    if game_config.game_mode == GameMode.MANUAL:
        _run_manual_mode(game_config, process_config)
    else:
        _run_ml_mode(game_config, process_config)

def _preprocess_process_config(process_config, game_defined_config):
    """
    Replace the some string value in `process_config` to usable objects
    """
    # Replace the function name to the function defined in the game_defined_config
    target_function = process_config["game"]["target"]
    if isinstance(target_function, str):
        process_config["game"]["target"] = game_defined_config.__dict__[target_function]

def _run_manual_mode(game_config: GameConfig, process_config):
    """
    Execute the game specified in manual mode
    """
    game_process_config = process_config["game"]

    # Append "game_config" at the beginning of function arguments
    args = (game_config, ) + game_process_config.get("args", ())
    kwargs = game_process_config.get("kwargs", {})

    game_process_config["target"](*args, **kwargs)

def _run_ml_mode(game_config: GameConfig, process_config):
    """
    Execute the game specified in ml mode
    """
    from .process import ProcessManager

    process_manager = ProcessManager()

    # Set game process #

    game_process_config = process_config["game"]
    args = (game_config, ) + game_process_config.get("args", ())
    kwargs = game_process_config.get("kwargs", {})

    process_manager.set_game_process(game_process_config["target"], args, kwargs)

    # Set ml processes #

    ml_process_names = [key for key in process_config.keys() if key != "game"]
    for i in range(len(ml_process_names)):
        process_name = ml_process_names[i]
        args = process_config[process_name].get("args", ())
        kwargs = process_config[process_name].get("kwargs", {})

        # Assign the input modules to the ml processes
        # If the number of provided modules is less than the number of processes,
        # the last module is assigned to the rest processes.
        module_id = (i if i < len(game_config.input_modules)
            else len(game_config.input_modules) - 1)

        process_manager.add_ml_process(game_config.input_modules[module_id],
            process_name, args, kwargs)

    process_manager.start()
