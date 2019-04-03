from optparse import OptionParser
from _version import version
import importlib

def create_optparser():
	usage_str = "python %prog [options] <game> [game_params]"
	description_str = \
		"\"game\" is the name of the game. " \
		"\"game_params\" is an optional parameter (not needed " \
		"by every game) to specify the additional setting for the game."

	parser = OptionParser(usage = usage_str, description = description_str, \
		version = version)
	parser.add_option("-f", "--fps", \
		action = "store", type = "int", dest = "fps", default = 30, \
		help = "the updating rate of the game process [default: %default]")
	parser.add_option("-m", "--manual", \
		action = "store_true", dest = "manual_mode", default = False, \
		help = "start the game in the manual mode instead of " \
		"the machine learning mode [default: %default]")
	parser.add_option("-r", "--record", \
		action = "store_true", dest = "record_progress", default = False, \
		help = "pickle the game progress (a list of scene info) to the log files "\
		"[default: %default]")
	parser.add_option("-1", "--one-shot", \
		action = "store_true", dest = "one_shot_mode", default = False, \
		help = "quit the game when the game is passed or over. " \
		"Only supported in the ml mode. [default: %default]")
	parser.add_option("-i", "--input-script", \
		action = "store", type = "str", dest = "input_script", default = "ml_play.py", \
		help = "specify the script used in the machine learning mode. " \
		"The script must have function `ml_loop()` and " \
		"be put in the <game>/ml directory. [default: %default]")

	return parser

def has_ml_script(game_name: str, script_name: str):
	import os.path

	dir_path = os.path.dirname(__file__)
	ml_script_path = os.path.join(dir_path, "{}/ml/{}".format(game_name, script_name))

	return os.path.exists(ml_script_path)

if __name__ == "__main__":
	optparser = create_optparser()
	(options, args) = optparser.parse_args()

	try:
		game_name = args[0].lower()
		game_params = args[1:]
		game = importlib.import_module("{}.main".format(game_name))

		if not options.manual_mode and \
		   not has_ml_script(game_name, options.input_script):
			raise FileNotFoundError

	except IndexError:
		print("Error: <game> is not specified. Use -h to see help.")
		print(optparser.get_usage()[:-1])
	except ModuleNotFoundError:
		print("Error: Game \"{}\" is not found.".format(game_name))
	except FileNotFoundError:
		print("Error: The script \"{}/ml/{}\" is not provided. " \
			"Cannot start the machine learning mode." \
			.format(game_name, options.input_script))
	else:
		game.execute(options, *game_params)
