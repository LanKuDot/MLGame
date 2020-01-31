from mlgame import gameconfig
from mlgame.exception import GameConfigError
import importlib

if __name__ == "__main__":
    try:
        config = gameconfig.get_game_config()
        game = importlib.import_module("games.{}.main".format(config.game_name))

        if config.game_mode == gameconfig.GameMode.MANUAL:
            game_execution = game.manual_mode
        elif config.game_mode == gameconfig.GameMode.ML:
            game_execution = game.ml_mode
    except GameConfigError as e:
        print("Error: " + str(e))
    except ModuleNotFoundError:
        print("Error: Game \"{}\" is not found.".format(config.game_name))
    except AttributeError as e:
        print("Error: Game \"{}\" does not provide {} mode." \
            .format(config.game_name, config.game_mode.name.lower()))
    else:
        game_execution(config)
