from argparse import ArgumentParser
from enum import Enum, auto
import os.path

from ._version import version

def get_command_parser():
	"""
	Generate an ArgumentParser for parse the arguments in the command line
	"""
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
		default = None, metavar = "ONLINE_CHANNEL", \
		help = "specify the remote server and the channel name with the format " \
		"\"<server_ip>:<server_port>:<channel_name>\", and " \
		"start the game in the online mode [default : %(default)s]")

	return parser

def get_game_config():
	"""
	Parse the command line and generate the GameConfig from the parsed result
	"""
	parser = get_command_parser()
	return GameConfig(parser.parse_args())

class GameMode(Enum):
	"""
	The mode of the game
	"""
	__slots__ = ()

	MANUAL = auto()
	ML = auto()
	ONLINE = auto()

class GameConfig:
	"""
	The data class for storing the configuration of the game

	@var game_name The name of the game to be executed
	@var game_params A list of parameters for the game
	@var one_shot_mode Whether to execute the game for only once
	@var game_mode The mode of the game to be executed
	@var record_progress Whether to record the game progress
	@var online_channel The information of the remote server
	     This member could be None, if the game_mode is not GameMode.ONLINE.
	@var fps The FPS of the game
	@var input_scripts A list of user scripts for running the ML mode
	"""

	def __init__(self, parsed_args):
		"""
		Generate the game configuration from the parsed command line arguments
		"""
		self.game_name = parsed_args.game[0]
		self.game_params = parsed_args.game_params

		self.one_shot_mode = parsed_args.one_shot_mode
		self.game_mode = self.get_game_mode(parsed_args)
		self.record_progress = parsed_args.record_progress
		self.online_channel = self.get_online_channel(parsed_args.online_channel)

		self.fps = parsed_args.fps
		self.input_scripts = self.get_ml_scripts(parsed_args.input_script)

	def get_game_mode(self, parsed_args):
		"""
		Judge the game mode according to the parsed arguments
		"""
		if parsed_args.manual_mode:
			return GameMode.MANUAL

		if parsed_args.online_channel:
			# In online mode, the game always only runs once
			self.one_shot_mode = True
			return GameMode.ONLINE

		return GameMode.ML

	def get_ml_scripts(self, input_scripts):
		"""
		Check whether the provided input scripts are all existing or not.

		If it passes, return a list of input scripts.
		Otherwise, raise the FileNotFoundError.
		"""
		top_dir_path = os.path.dirname(os.path.dirname(__file__))

		for script_name in input_scripts:
			script_path = os.path.join(top_dir_path, self.game_name,
				"ml", script_name)

			if not os.path.exists(script_path):
				raise FileNotFoundError( \
					"The script \"{}/ml/{}\" does not exist. " \
					"Cannot start the game." \
					.format(self.game_name, script_name))

		return input_scripts

	def get_online_channel(self, channel_str):
		"""
		Check the format of the channel information string

		If it passes, return the parsed channel information.
		Otherwise, raise ValueError.
		"""
		if not channel_str:
			return None

		splited_str = channel_str.split(":")
		if len(splited_str) != 3:
			raise ValueError("Invalid ONLINE_CHANNEL format. Must be " \
				"\"<server_ip>:<server_port>:<channel_nane>\".")
		return splited_str

	def __str__(self):
		return "{" + \
			"'game_name': '{}', ".format(self.game_name) + \
			"'game_params': {}, ".format(self.game_params) + \
			"'game_mode': {}, ".format(self.game_mode) + \
			"'one_shot_mode': {}, ".format(self.one_shot_mode) + \
			"'record_progress': {}, ".format(self.record_progress) + \
			"'online_channel': {}, ".format(self.online_channel) + \
			"'fps': {}, ".format(self.fps) + \
			"'input_scripts': {}".format(self.input_scripts)
