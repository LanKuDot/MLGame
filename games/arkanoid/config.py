GAME_VERSION = "1.0"
GAME_PARAMS = {
    "()": {
        "prog": "arkanoid",
        "game_usage": "%(prog)s <difficulty> <level>"
    },
    "difficulty": {
        "choices": ("EASY", "NORMAL"),
        "metavar": "difficulty",
        "help": "Specify the game style. Choices: %(choices)s"
    },
    "level": {
        "type": int,
        "help": "Specify the level map"
    }
}

PROCESSES = {
    "manual_mode": {
        "game": {
            "target": "run_game",
            "args": (False, )
        }
    },
    "ml_mode": {
        "game": {
            "target": "run_game",
            "args": (True, )
        },
        "ml": {}
    }
}

def run_game(game_config, run_ml_mode):
    if run_ml_mode:
        from .game.arkanoid_ml import Arkanoid
    else:
        from .game.arkanoid import Arkanoid

    game = Arkanoid(game_config.fps,
        game_config.game_params.difficulty, game_config.game_params.level,
        game_config.record_progress, game_config.one_shot_mode)
    game.game_loop()
