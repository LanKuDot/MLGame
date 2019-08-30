from mlgame.gameconfig import GameConfig

def ml_mode(config: GameConfig):
    """
    Start the game in the machine learning mode
    """
    game_over_score = _get_game_over_score(config.game_params, config.one_shot_mode)
    module_1P, module_2P = _get_ml_modules(config.input_modules)

    from mlgame.process import ProcessManager

    process_manager = ProcessManager()
    process_manager.set_game_process(_start_game_process, \
        args = (config.fps, game_over_score, \
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

def _start_game_process(fps, game_over_score, record_progress):
    """
    Start the process to run the game core

    @param fps The updating rate of the game
    """
    from .game.pingpong_ml import PingPong

    game = PingPong(fps, game_over_score, record_progress)
    game.game_loop()

def manual_mode(config: GameConfig):
    """
    Play the game as a normal game
    """
    from .game.pingpong import PingPong

    game_over_score = _get_game_over_score(config.game_params, config.one_shot_mode)

    game = PingPong(config.fps, game_over_score, config.record_progress)
    game.game_loop()

def _get_game_over_score(game_params, one_shot_mode):
    """
    Get game over score from the parameter
    """
    if one_shot_mode:
        print("One shot mode is on. Set game-over score to 1.")
        return 1

    try:
        game_over_score = int(game_params[0])
        if game_over_score < 1:
            raise ValueError
    except IndexError:
        print("Game-over score is not specified. Set to 3.")
        game_over_score = 3
    except ValueError:
        print("Invalid game-over score. Set to 3.")
        game_over_score = 3

    return game_over_score

def get_log_dir():
    import os.path
    return os.path.join(os.path.dirname(__file__), "log")
