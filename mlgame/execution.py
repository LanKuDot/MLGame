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
from .gameconfig import GameConfig
from .loops import GameMLModeExecutorProperty, MLExecutorProperty
from .utils.argparser_generator import get_parser_from_dict
from . import errno

def execute():
    """
    Parse the execution command and execute the game
    """
    try:
        execution_cmd, game_config = _parse_command_line()
    except (ExecutionCommandError, GameConfigError) as e:
        print("Error:", e)
        sys.exit(errno.COMMAND_LINE_ERROR)

    if execution_cmd.game_mode == GameMode.MANUAL:
        _run_manual_mode(execution_cmd, game_config.game_setup)
    else:
        _run_ml_mode(execution_cmd, game_config.game_setup)

def _parse_command_line():
    """
    Parse the command line arguments

    If "-h/--help" or "-l/--list" flag is specfied, it will print the related message
    and exit the program.

    @return A tuple of (`ExecutionCommand` object, `GameConfig` object)
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

    # Load the game defined config
    game_config = GameConfig(parsed_args.game)

    # Create game_param parser
    param_parser = get_parser_from_dict(game_config.game_params)
    parsed_game_params = param_parser.parse_args(parsed_args.game_params)

    # Replace the input game_params with the parsed one
    parsed_args.game_params = [value for value in vars(parsed_game_params).values()]

    # Generate execution command
    try:
        exec_cmd = ExecutionCommand(parsed_args)
    except ExecutionCommandError:
        raise

    return exec_cmd, game_config

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

def _run_manual_mode(execution_cmd: ExecutionCommand, game_setup):
    """
    Execute the game specified in manual mode

    @param execution_cmd The `ExecutionCommand` object
    @param game_setup The `GAME_SETUP` defined in the game config
    """
    from .loops import GameManualModeExecutor
    from .exceptions import GameProcessError

    # Collect ml names
    ml_names = []
    for client in game_setup["ml_clients"]:
        ml_names.append(client["name"])

    game_cls = game_setup["game"]
    try:
        executor = GameManualModeExecutor(execution_cmd, game_cls, ml_names)
        executor.start()
    except GameProcessError as e:
        print("Error: Exception occurred in 'game' process:")
        print(e.message)
        sys.exit(errno.GAME_EXECUTION_ERROR)

def _run_ml_mode(execution_cmd: ExecutionCommand, game_setup):
    """
    Execute the game specified in ml mode

    @param execution_cmd The `ExecutionCommand` object
    @param game_setup The `GAME_SETUP` defined in the game config
    """
    from .process import ProcessManager

    game_propty = _get_game_executor_propty(execution_cmd, game_setup)
    ml_propties = _get_ml_executor_propties(execution_cmd, game_setup)

    process_manager = ProcessManager(game_propty, ml_propties)
    returncode = process_manager.start()
    if returncode == -1:
        sys.exit(errno.GAME_EXECUTION_ERROR)

def _get_game_executor_propty(
        execution_cmd: ExecutionCommand, game_setup) -> GameMLModeExecutorProperty:
    """
    Get the property for the game executor in the ml mode
    """
    game_cls = game_setup["game"]
    ml_clients = game_setup["ml_clients"]
    ml_names = []
    for client in ml_clients:
        ml_names.append(client["name"])

    return GameMLModeExecutorProperty(
        "game", execution_cmd, game_cls, ml_names)

def _get_ml_executor_propties(execution_cmd: ExecutionCommand, game_setup) -> list:
    """
    Get the property for the ml executors

    @return A list of generated properties
    """
    propties = []
    ml_clients = game_setup["ml_clients"]
    dynamic_ml_clients = game_setup["dynamic_ml_clients"]

    for i in range(len(ml_clients)):
        ml_client = ml_clients[i]

        ml_name = ml_client["name"]
        args = ml_client.get("args", ())
        kwargs = ml_client.get("kwargs", {})

        # Assign the input modules to the ml processes
        if dynamic_ml_clients and i == len(execution_cmd.input_modules):
            # If 'dynamic_ml_client' is set, then the number of ml clients
            # is decided by the number of input modules.
            break
        else:
            # If the number of provided modules is less than the number of processes,
            # the last module is assigned to the rest processes.
            module_id = (i if i < len(execution_cmd.input_modules)
                else len(execution_cmd.input_modules) - 1)
            ml_module = execution_cmd.input_modules[module_id]

        # Compile the non-python script
        # It is stored as a (crosslang ml client module, non-python script) tuple.
        if isinstance(ml_module, tuple):
            non_py_script = ml_module[1]
            ml_module = ml_module[0]
            # Wrap arguments passed to be passed to the script
            module_kwargs = {
                "script_execution_cmd": _compile_non_py_script(non_py_script),
                "init_args": args,
                "init_kwargs": kwargs
            }
            args = ()
            kwargs = module_kwargs

        propties.append(MLExecutorProperty(ml_name, ml_module, args, kwargs))

    return propties

def _compile_non_py_script(script_path):
    """
    Compile the non-python script and return the execution command for the script

    @return A list of command segments for executing the compiled script
    """
    try:
        print("Compiling '{}'...".format(script_path), end = " ", flush = True)
        script_execution_cmd = compile_script(script_path)
    except CompilationError as e:
        print("Failed\nError: {}".format(e))
        sys.exit(errno.COMPILATION_ERROR)
    print("OK")

    return script_execution_cmd
