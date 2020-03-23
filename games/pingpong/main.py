from mlgame.gameconfig import GameConfig
from mlgame.exception import GameParameterError

from .game.gamecore import Difficulty

def ml_mode(config: GameConfig):
    """
    Start the game in the machine learning mode
    """
    try:
        difficulty, game_over_score = (
            _get_difficulty_and_score(config.game_params, config.one_shot_mode))
    except GameParameterError as e:
        print("Error: " + str(e), usage(), sep = "\n")
        return

    module_1P, module_2P = _get_ml_modules(config.input_modules)

    from mlgame.process import ProcessManager

    process_manager = ProcessManager()
    process_manager.set_game_process(_start_game_process,
        args = (config.fps, difficulty, game_over_score,
        config.record_progress))
    process_manager.add_ml_process(module_1P, "ml_1P", args = ("1P", ))
    process_manager.add_ml_process(module_2P, "ml_2P", args = ("2P", ))

    process_manager.start()

def _get_ml_modules(input_modules):
    """
    Get the modules for 1P and 2P

    If only 1 input module specified, 1P and 2P use the same module.
    """
    if len(input_modules) == 1:
        return input_modules[0], input_modules[0]

    return input_modules[0], input_modules[1]

def _start_game_process(fps, difficulty, game_over_score, record_progress):
    """
    Start the process to run the game core

    @param fps The updating rate of the game
    """
    from .game.pingpong_ml import PingPong

    game = PingPong(fps, difficulty, game_over_score, record_progress)
    game.game_loop()

def manual_mode(config: GameConfig):
    """
    Play the game as a normal game
    """
    from .game.pingpong import PingPong

    try:
        difficulty, game_over_score = (
            _get_difficulty_and_score(config.game_params, config.one_shot_mode))
    except GameParameterError as e:
        print("Error: " + str(e), usage(), sep = "\n")
        return

    game = PingPong(config.fps, difficulty, game_over_score, config.record_progress)
    game.game_loop()

def _get_difficulty_and_score(game_params, one_shot_mode):
    """
    Get game over score from the parameter
    """
    try:
        difficulty_str = str(game_params[0]).upper()
        difficulty = Difficulty(difficulty_str)
    except IndexError:
        raise GameParameterError("'difficulty' is not specified.")
    except ValueError:
        raise GameParameterError("The value of 'difficulty' is invalid.")

    if one_shot_mode:
        print("One shot mode is on. Set game_over_score to 1.")
        return difficulty_str, 1

    try:
        game_over_score = int(game_params[1])
        if game_over_score < 1:
            raise ValueError
    except IndexError:
        print("Game-over score is not specified. Set to 3.")
        game_over_score = 3
    except ValueError:
        print("Invalid game-over score. Set to 3.")
        game_over_score = 3

    return difficulty, game_over_score

def usage():
    return (
        "Usage: python MLGame.py pingpong <difficulty> [game_over_score]\n" +
        "Game parameters:\n" +
        "- difficulty: The game style. Should be 'EASY', 'NORMAL' or 'HARD'\n" +
        "- game_over_score: [Optional] The score that the game will exit when either side " +
        "reaches")
