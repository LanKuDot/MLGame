import os.path

def ml_mode(config):
    from mlgame.process import ProcessManager

    process_manager = ProcessManager()
    process_manager.set_game_process(_start_game_process, \
        args = (config.fps, config.one_shot_mode, \
        config.record_progress))
    process_manager.add_ml_process(config.input_modules[0], "ml")

    process_manager.start()

def _start_game_process(fps, one_shot_mode, record_progress):
    from .game.snake_ml import Snake

    game = Snake(fps, one_shot_mode, record_progress)
    game.game_loop()

def manual_mode(config):
    from .game.snake import Snake

    game = Snake(config.fps, config.one_shot_mode, config.record_progress)
    game.game_loop()

def get_log_dir():
    return os.path.join(os.path.dirname(__file__), "log")
