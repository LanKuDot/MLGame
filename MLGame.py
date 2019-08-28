from essential import gameconfig
import importlib

if __name__ == "__main__":
	try:
		config = gameconfig.get_game_config()
		game = importlib.import_module("games.{}.main".format(config.game_name))

		if config.game_mode == gameconfig.GameMode.MANUAL:
			game.manual_mode(config)
		elif config.game_mode == gameconfig.GameMode.ML:
			game.ml_mode(config)
	except ModuleNotFoundError:
		print("Error: Game \"{}\" is not found.".format(config.game_name))
	except AttributeError:
		print("Error: Game \"{}\" does not provide {} mode." \
			.format(config.game_name, config.game_mode.name.lower()))
