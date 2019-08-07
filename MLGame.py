from essential import gameconfig
import importlib

if __name__ == "__main__":
	try:
		config = gameconfig.get_game_config()
		game = importlib.import_module("{}.main".format(config.game_name))
	except ModuleNotFoundError:
		print("Error: Game \"{}\" is not found.".format(config.game_name))
	else:
		game.execute(config)
