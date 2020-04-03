from argparse import ArgumentTypeError

def positive_int(string):
    value = int(string)
    if value < 1:
        raise ArgumentTypeError()
    return value

GAME_PARAMS = {
    "()": {
        "prog": "pingpong",
        "game_usage": "%(prog)s <difficulty> [game_over_score]"
    },
    "difficulty": {
        "choices": ("EASY", "NORMAL", "HARD"),
        "metavar": "difficulty",
        "help": "Specify the game style. Choices: %(choices)s"
    },
    "game_over_score": {
        "type": positive_int,
        "nargs": "?",
        "default": 3,
        "help": ("[Optional] The score that the game will be exited "
            "when either side reaches it.[default: %(default)s]")
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
        "ml_1P": {
            "args": ("1P", )
        },
        "ml_2P": {
            "args": ("2P", )
        }
    }
}

def run_game(game_config, run_ml_mode):
    if run_ml_mode:
        from .game.pingpong_ml import PingPong
    else:
        from .game.pingpong import PingPong

    if game_config.one_shot_mode:
        game_config.game_params.game_over_score = 1
        print("One shot mode is on. Set 'game_over_score' to 1.")

    game = PingPong(game_config.fps,
        game_config.game_params.difficulty, game_config.game_params.game_over_score,
        game_config.record_progress)
    game.game_loop()
