from mlgame.gameconfig import GameConfig

def ml_mode(config: GameConfig):
    """Start the game in the machine learning mode

    Create a game and a machine learning processes.
    """
    level = _get_level(config.game_params)
    to_transition = True if config.transition_channel else False

    from mlgame.process import ProcessManager

    process_manager = ProcessManager()
    process_manager.set_game_process(_start_game_process, \
        args = (config.fps, level, \
        config.record_progress, config.one_shot_mode, to_transition))
    process_manager.add_ml_process(config.input_modules[0], "ml")

    if to_transition:
        process_manager.set_transition_process(*config.transition_channel)

    process_manager.start()

def _start_game_process(fps, level, record_progress, one_shot_mode, to_transition):
    """Start the game process

    @param fps Specify the updating rate of the game
    @param level Specify the level of the game
    @param record_progress Whether to record the game progress
    @param one_shot_mode Whether to run the game for only one round
    @param to_transition Whether to pass the game progress to transition process
    """
    from .game.arkanoid_ml import Arkanoid

    game = Arkanoid(fps, level, record_progress, one_shot_mode, to_transition)
    game.game_loop()

def manual_mode(config: GameConfig):
    """Play the game as a normal game
    """
    from .game.arkanoid import Arkanoid

    level = _get_level(config.game_params)

    game = Arkanoid(config.fps, level, config.record_progress, config.one_shot_mode)
    game.game_loop()

def _get_level(game_params):
    """Get the level from the parameter
    """
    try:
        level = int(game_params[0])
        if level < 1:
            raise ValueError
    except IndexError:
        print("Level is not specified. Set to 1.")
        level = 1
    except ValueError:
        print("Invalid level value. Set to 1.")
        level = 1

    return level

def get_log_dir():
    import os.path
    return os.path.join(os.path.dirname(__file__), "log")