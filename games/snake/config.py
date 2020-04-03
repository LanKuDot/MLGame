def run_game(game_config, run_ml_mode):
    if run_ml_mode:
        from .game.snake_ml import Snake
    else:
        from .game.snake import Snake

    game = Snake(game_config.fps, game_config.one_shot_mode,
        game_config.record_progress)
    game.game_loop()

PROCESSES = {
    "manual_mode": {
        "game": {
            "target": run_game,
            "args": (False, )
        }
    },
    "ml_mode": {
        "game": {
            "target": run_game,
            "args": (True, )
        },
        "ml": {}
    }
}