from mlgame.gameconfig import GameConfig
from mlgame.exception import GameParameterError

def ml_mode(config: GameConfig):
    """
    Start the game in the machine learning mode

    Create a game and a machine learning processes.
    """
    try:
        difficulty, level = _get_difficulty_and_level(config.game_params)
    except GameParameterError as e:
        print("Error: " + str(e) + "\n" + usage())
        return

    from mlgame.process import ProcessManager

    process_manager = ProcessManager()
    process_manager.set_game_process(_start_game_process, \
        args = (config.fps, difficulty, level, \
        config.record_progress, config.one_shot_mode))
    process_manager.add_ml_process(config.input_modules[0], "ml")

    process_manager.start()

def _start_game_process(fps, difficulty, level, record_progress, one_shot_mode):
    """
    Start the game process

    @param fps Specify the updating rate of the game
    @param difficulty Specify the difficulty of the game
    @param level Specify the level of the game
    @param record_progress Whether to record the game progress
    @param one_shot_mode Whether to run the game for only one round
    """
    from .game.arkanoid_ml import Arkanoid

    game = Arkanoid(fps, difficulty, level, record_progress, one_shot_mode)
    game.game_loop()

def manual_mode(config: GameConfig):
    """
    Play the game as a normal game
    """
    try:
        difficulty, level = _get_difficulty_and_level(config.game_params)
    except GameParameterError as e:
        print("Error: " + str(e) + "\n" + usage())
        return

    from .game.arkanoid import Arkanoid

    game = Arkanoid(config.fps, difficulty, level, \
        config.record_progress, config.one_shot_mode)
    game.game_loop()

def _get_difficulty_and_level(game_params):
    """
    Get the difficulty and level from the parameter
    """
    from .game.gamecore import Difficulty
    # Get difficulty
    try:
        difficulty = str(game_params[0]).upper()
        if difficulty not in list(Difficulty):
            raise ValueError
    except IndexError:
        raise GameParameterError("'difficulty' is not specified.")
    except ValueErrore:
        raise GameParameterError("'difficulty' is invalid.")

    # Get level
    try:
        level = int(game_params[1])
        if level < 1:
            raise ValueError
    except IndexError:
        raise GameParameterError("'level' is not specified")
    except ValueError:
        raise GameParameterError("'level' is invalid.")

    return difficulty, level

def usage():
    return \
        "Usage: python MLGame.py arkanoid <difficulty> <level>\n" + \
        "Game parameters:\n" +\
        "- difficulty: The game style. Should be 'EASY' or 'NORMAL'\n" +\
        "- level: The game level."