from optparse import OptionParser
import importlib

def create_optparser():
	usage_str = "python %prog [options] <game> [game_level]"
	description_str = \
		"\"game\" is the name of the game. " \
		"\"game_level\" is an optional argument (not needed " \
		"by every game) to specify the level of the game."

	parser = OptionParser(usage = usage_str, description = description_str)
	parser.add_option("-f", "--fps", \
		action = "store", type = "int", dest = "fps", default = 30, \
		help = "the updating rate of the game process [default: %default]")
	parser.add_option("-m", "--manual", \
		action = "store_true", dest = "manual_mode", default = False, \
		help = "start the game in the manual mode instead of " \
		"the machine learning mode [default: %default]")
	
	return parser

if __name__ == "__main__":
	optparser = create_optparser()
	(options, args) = optparser.parse_args()

	game_name = args[0].lower()
	game_options = args[1:]
	game = importlib.import_module("{}.main".format(game_name))

	if options.manual_mode:
		game.manual_mode(options.fps, *game_options)
	else:
		game.ml_mode(options.fps, *game_options)
