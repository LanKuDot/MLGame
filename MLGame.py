from argparse import ArgumentParser
from _version import version
import importlib

def create_argparser():
	usage_str = "python %(prog)s [options] <game> [game_params]"
	description_str = "A platform for applying machine learning algorithm " \
		"to play pixel games"

	parser = ArgumentParser(usage = usage_str, description = description_str)

	parser.add_argument("game", type = str, nargs = 1, \
		help = "the name of the game to be started")
	parser.add_argument("game_params", nargs = '*', default = None, \
		help = "the additional settings for the game")

	parser.add_argument("--version", action = "version", version = version)
	parser.add_argument("-f", "--fps", type = int, default = 30, \
		help = "the updating frequency of the game process [default: %(default)s]")
	parser.add_argument("-m", "--manual-mode", action = "store_true", default = False, \
		help = "start the game in the manual mode instead of " \
		"the machine learning mode [default: %(default)s]")
	parser.add_argument("-r", "--record", action = "store_true", \
		dest = "record_progress", default = False, \
		help = "pickle the game progress (a list of SceneInfo) to the log file. " \
		"One file for a round, and stored in \"<game>/log/\" directory. " \
		"[default: %(default)s]")
	parser.add_argument("-1", "--one-shot", action = "store_true", \
		dest = "one_shot_mode", default = False, \
		help = "quit the game when the game is passed or is over. " \
		"Otherwise, the game will restart automatically. " \
		"Only supported in the machine learning mode. [default: %(default)s]")
	# TODO: Set the default script to the ml_play_template.py
	parser.add_argument("-i", "--input-script", type = str, nargs = '+', \
		default = ["ml_play.py"], metavar = "SCRIPT", \
		help = "specify the script(s) used in the machine learning mode. " \
		"The script must have function `ml_loop()` and " \
		"be put in the \"<game>/ml/\" directory. [default: %(default)s]")
	parser.add_argument("--online-channel", type = str, \
		default = None, metavar = "SERVER_INFO", \
		help = "specify the remote server and the channel name with the format " \
		"\"<server_ip>:<server_port>:<channel_name>\", and " \
		"start the game in the online mode [default : %(default)s]")

	return parser

def has_ml_script(game_name: str, script_name: str):
	import os.path

	dir_path = os.path.dirname(__file__)
	ml_script_path = os.path.join(dir_path, "{}/ml/{}".format(game_name, script_name))

	return os.path.exists(ml_script_path)

if __name__ == "__main__":
	parser = create_argparser()
	options = parser.parse_args()

	try:
		game_name = options.game[0]
		game = importlib.import_module("{}.main".format(game_name))

		if not options.manual_mode:
			for script in options.input_script:
				if not has_ml_script(game_name, script):
					raise FileNotFoundError(script)

	except IndexError:
		print("Error: <game> is not specified. Use -h to see help.")
		print(optparser.get_usage()[:-1])
	except ModuleNotFoundError:
		print("Error: Game \"{}\" is not found.".format(game_name))
	except FileNotFoundError as e:
		print("Error: The script \"{}/ml/{}\" is not provided. " \
			"Cannot start the machine learning mode." \
			.format(game_name, e.args[0]))
	else:
		game.execute(options)
