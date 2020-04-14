"""
Parse the execution command, load the game config, and execute the game
"""
import importlib
import os
import os.path
import sys

from .crosslang.main import compile_script
from .gameconfig import get_command_parser, GameMode, GameConfig
from .exception import GameConfigError, CompilationError
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

    This function will load `GAME_PARAMS` defined in the "config.py" in the game
    directory to generate a parser for parsing the game parameters.
    If it cannot find `GAME_PARAMS`, it will generate a default parser.
    Refer `mlgame.utils.argparser_generator` for the format of the `GAME_PARAMS`.

    A special case is that specifying "game_usage" to "()" in `GAME_PARAMS`.
    The program will append the usage of `MLGame.py` to the "game_usage" and
    assign it to the "usage".

    @return A `GameConfig` object
    """
    # Parse the command line arguments
    cmd_parser = get_command_parser()
    parsed_args = cmd_parser.parse_args()

    ## Functional print ##
    # If "-h/--help" is specified, print help message and exit.
    if parsed_args.help:
        cmd_parser.print_help()
        sys.exit(0)
    # If "-l/--list" is specified, list available games and exit.
    elif parsed_args.list_games:
        _list_games()
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
    _preprocess_game_param_dict(game_defined_params, game_defined_config)
    param_parser = get_parser_from_dict(game_defined_params)

    # Replace the input game_params with the parsed one
    parsed_args.game_params = param_parser.parse_args(parsed_args.game_params)

    # Generate GameConfig
    try:
        config = GameConfig(parsed_args)
    except Exception as e:
        raise GameConfigError(str(e))

    return config

def _list_games():
    """
    List available games which provide "config.py" in the game directory.
    """
    game_root_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "games")
    dirs = [f for f in os.listdir(game_root_dir)
        if ("__" not in f) and (os.path.isdir(os.path.join(game_root_dir, f)))]

    game_info_list = [("Game", "Version"), ("-----", "-----")]
    max_name_len = 5
    # Load the config and version
    for game_dir in dirs:
        try:
            game_defined_config = importlib.import_module(
                "games.{}.config".format(game_dir))
            game_version = game_defined_config.GAME_VERSION
        except ModuleNotFoundError:
            continue
        except AttributeError:
            game_version = ""

        game_info_list.append((game_dir, game_version))
        max_name_len = max(max_name_len, len(game_dir))

    for name, version in game_info_list:
        print(name.ljust(max_name_len + 1), version)

def _preprocess_game_param_dict(param_dict, game_defined_config):
    """
    Preprocess the game defined `GAME_PARAMS`
    """
    # Append the command of MLGame to the `game_usage`
    # and set it to the `usage`
    if (param_dict.get("()") and
        param_dict["()"].get("game_usage")):
        game_usage = str(param_dict["()"].pop("game_usage"))
        param_dict["()"]["usage"] = (
            "python MLGame.py [options] " + game_usage)

    # If the game not specify "--version" flag,
    # try to convert `GAME_VERSION` to a flag
    if not param_dict.get("--version"):
        try:
            game_version = str(game_defined_config.GAME_VERSION)
        except AttributeError:
            game_version = ""

        param_dict["--version"] = {
            "action": "version",
            "version": game_version
        }

def _game_execution(game_config: GameConfig):
    """
    Execute the game

    This function will load the `PROCESSES` which specifies how to start the game
    from the "config.py" in the game directory. The `PROCESSES` is a dictionary which
    has 2 keys - "manual_mode" and "ml_mode", and the program will use either key
    according to the game mode.

    The value of the key "manual_mode" or "ml_mode" is a "process_config" which is
    a dictionary specifying how to start processes. The "process_config" for
    "manual_mode" has only a key "game" to specify how to start a game process.
    The value for the key "game" is also a dictionary which has 3 members:
    - "target": The entry function to start a game process. The value must be a
        callable. If it is a string, the program will try to find the function
        of the same name defined in the "config.py" of the game. The "target" must
        provide a parameter as the first parameter for the program to pass a
        `GameConfig` object.
    - "args": [Optional] The positional arguments to be passed to the "target".
        Should be a tuple or a list. The `GameConfig` object will be added as the
        first object in the "args" before invoking "target".
    - "kwargs": [Optional] The keyword arguments to be passed to the "target".
        Should be a dictionary.

    The "process_config" for the "ml_mode" is similar to the "manual_mode",
    but it has additional members for the ml processes. The key name is the name
    of the ml process, its value is similar to the "game"s', but it dosen't
    have the key "target", and the `GameConfig` object will not be added to
    the "args".

    An example of `PROCESSES`:
    ```python
    PROCESSES = {
        "manual_mode": {
            "game": {
                "target": "run_game",
                "args": ("foo", )
            }
        },
        "ml_mode": {
            "game": {
                "target": "run_game",
                "args": ("bar", )
            },
            "ml": {}
        }
    }

    def run_game(game_config, bar):
        print(bar)
    ```

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
        ml_module = game_config.input_modules[module_id]

        # Compile the non-python script
        # It is stored as a (crosslang ml client module, non-python script) tuple.
        if isinstance(ml_module, tuple):
            try:
                execution_cmd = compile_script(ml_module[1])
            except CompilationError as e:
                print("Error: {}".format(e))
                sys.exit(1)

            ml_module = ml_module[0]
            # Wrap arguments passed to be passed to the script
            module_kwargs = {
                "execution_cmd": execution_cmd,
                "init_args": args,
                "init_kwargs": kwargs
            }
            args = ()
            kwargs = module_kwargs

        process_manager.add_ml_process(ml_module, process_name, args, kwargs)

    returncode = process_manager.start()
    sys.exit(returncode)
