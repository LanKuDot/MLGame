"""
Parse the execution command, load the game config, and execute the game
"""
import importlib
import os
import os.path
import sys

from .crosslang.main import compile_script
from .crosslang.exceptions import CompilationError
from .execution_command import get_command_parser, GameMode, ExecutionCommand
from .exceptions import ExecutionCommandError, GameConfigError
from .utils.argparser_generator import get_parser_from_dict

def execute():
    """
    Parse the execution command and execute the game
    """
    try:
        execution_cmd = _get_execution_command()
    except (ExecutionCommandError, GameConfigError) as e:
        print("Error:", e)
        sys.exit(1)

    try:
        _game_execution(execution_cmd)
    except GameConfigError as e:
        print("Error:", e)
        sys.exit(1)

def _get_execution_command() -> ExecutionCommand:
    """
    Parse the execution command and generate `ExecutionCommand`

    This function will load `GAME_PARAMS` defined in the "config.py" in the game
    directory to generate a parser for parsing the game parameters specified in the command.
    If it cannot find `GAME_PARAMS`, it will generate a default parser.
    Refer `mlgame.utils.argparser_generator` for the format of the `GAME_PARAMS`.

    A special case is that specifying "game_usage" to "()" in `GAME_PARAMS`.
    The program will append the usage of `MLGame.py` to the "game_usage" and
    assign it to the "usage".

    @return A `ExecutionCommand` object
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
    parsed_game_params = param_parser.parse_args(parsed_args.game_params)

    # Replace the input game_params with the parsed one
    parsed_args.game_params = [value for value in vars(parsed_game_params).values()]

    # Generate execution command
    try:
        return ExecutionCommand(parsed_args)
    except ExecutionCommandError:
        raise

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

def _game_execution(execution_cmd: ExecutionCommand):
    """
    Execute the game

    This function will load the `GAME_SETUP` which specifies how to start the game
    from the "config.py" in the game directory. The `GAME_SETUP` is a dictionary which
    has several keys:
    - "game": Specify the class of the game to be execute
    - "keyboards": A list containing the mapping of key to the game command.
      Each mapping is a dictionary, the key is the keycode of pygame, the value is the
      command. One mapping per player (i.e. if the game has two players, then there is
      two mapping in the list). This field is used for the manual mode.
    - "ml_clients": A list containing the information of the ml client.
      Each element in the list is a dictionary in which members are:
      - "name": A string which is the name of the ml client.
      - "args": (Optional) A tuple which contains the initial positional arguments
        to be passed to the ml client.
      - "kwargs": (Optional) A dictionary which contains the initial keyword arguments
        to be passed to the ml client.

    @param execution_cmd The execution command
    """
    try:
        game_defined_config = importlib.import_module(
            "games.{}.config".format(execution_cmd.game_name))
        game_setup_config = game_defined_config.GAME_SETUP

        game_cls = game_setup_config["game"]
        keyboard_maps = game_setup_config["keyboards"]
        ml_clients = game_setup_config["ml_clients"]
    except AttributeError:
        raise GameConfigError("'GAME_SETUP' is not defined in '{}'"
            .format(game_defined_config.__name__))
    except KeyError as e:
        raise GameConfigError("{} is not found in 'GAME_SETUP'".format(e))

    if execution_cmd.game_mode == GameMode.MANUAL:
        _run_manual_mode(execution_cmd, game_cls, keyboard_maps)
    else:
        _run_ml_mode(execution_cmd, game_cls, ml_clients)

def _run_manual_mode(execution_cmd: ExecutionCommand, game_cls, keyboard_maps):
    """
    Execute the game specified in manual mode

    @param execution_cmd The `ExecutionCommand` object
    @param game_cls The class of the game to be executed
    @param keyboard_maps A list of mappings of keycode to command
    """
    from .loops import GameManualModeExecutor

    executor = GameManualModeExecutor(execution_cmd, game_cls, keyboard_maps)
    executor.start()

def _run_ml_mode(execution_cmd: ExecutionCommand, game_cls, ml_clients):
    """
    Execute the game specified in ml mode

    @param execution_cmd The `ExecutionCommand` object
    @param game_cls The class of the game to be executed
    @param ml_clients A list of configs of the ml clients
    """
    from .process import ProcessManager

    process_manager = ProcessManager()

    # Set game process
    process_manager.set_game_process(execution_cmd, game_cls)

    # Set ml processes
    for i in range(len(ml_clients)):
        ml_client = ml_clients[i]

        process_name = ml_client["name"]
        args = ml_client.get("args", ())
        kwargs = ml_client.get("kwargs", {})

        # Assign the input modules to the ml processes
        # If the number of provided modules is less than the number of processes,
        # the last module is assigned to the rest processes.
        module_id = (i if i < len(execution_cmd.input_modules)
            else len(execution_cmd.input_modules) - 1)
        ml_module = execution_cmd.input_modules[module_id]

        # Compile the non-python script
        # It is stored as a (crosslang ml client module, non-python script) tuple.
        if isinstance(ml_module, tuple):
            try:
                print("Compiling '{}'...".format(ml_module[1]), end = " ", flush = True)
                script_execution_cmd = compile_script(ml_module[1])
            except CompilationError as e:
                print("Failed\nError: {}".format(e))
                sys.exit(1)
            print("OK")

            ml_module = ml_module[0]
            # Wrap arguments passed to be passed to the script
            module_kwargs = {
                "script_execution_cmd": script_execution_cmd,
                "init_args": args,
                "init_kwargs": kwargs
            }
            args = ()
            kwargs = module_kwargs

        process_manager.add_ml_process(process_name, ml_module, args, kwargs)

    returncode = process_manager.start()
    sys.exit(returncode)
