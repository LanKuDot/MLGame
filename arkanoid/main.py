from essential.gameconfig import GameMode

def execute(config):
	"""Start the game in the selected mode

	An additional game parameter (stored in options.game_params)
	for the game arkanoid is the level.

	@param config The game configuration specified in the command line
	"""
	try:
		level = int(config.game_params[0])
		if level < 1:
			raise ValueError
	except IndexError:
		print("Level is not specified. Set to 1.")
		level = 1
	except ValueError:
		print("Invalid level value. Set to 1.")
		level = 1

	if config.game_mode == GameMode.MANUAL:
		_manual_mode(config.fps, level, config.record_progress)
	else:
		_ml_mode(config.fps, level, config.input_scripts[0], \
			config.record_progress, config.one_shot_mode, \
			config.transition_channel)

def _ml_mode(fps, level, input_script = "ml_play_template.py", \
	record_progress = False, one_shot_mode = False, transition_channel = None):
	"""Start the game in the machine learning mode

	Create a game and a machine learning processes.
	The main process will run the game process.
	If the `server_info` is not None, the main process will be the transition process,
	which will pass the game progress to the remote server.

	After quit from the drawing loop,
	the created processes will be terminated.

	@param fps Specify the updating rate of the game
	@param level Specify the level of the game
	@param input_script Specify the script for the ml process
	@param record_progress Specify whether to record the game progress or not
	@param one_shot_mode Specify whether to run the game only once or not
	@param transition_channel Specify a list [server_ip, server_port, channel_name]
	"""
	to_transition = True if transition_channel else False

	from essential.process import ProcessManager

	process_manager = ProcessManager()
	process_manager.set_game_process(_start_game_process, \
		args = (fps, level, record_progress, one_shot_mode, to_transition))
	process_manager.add_ml_process("arkanoid.ml.{}".format(input_script.split('.')[0]), "ml")

	if transition_channel:
		process_manager.set_transition_process(*transition_channel)

	process_manager.start()

def _start_game_process(fps, level, record_progress, one_shot_mode, to_transition):
	"""Start the game process

	@param fps Specify the updating rate of the game
	@param level Specify the level of the game
	@param record_progress Whether to record the game progress
	@param one_shot_mode Whether to run the game for only one round
	@param to_transition Whether to pass the game progress to transition process
	"""
	from .game.arkanoid_ml import Arkanoid

	record_handler = _get_record_handler(record_progress)
	game = Arkanoid(fps, level, record_handler, one_shot_mode, to_transition)
	game.game_loop()

def _manual_mode(fps, level, record_progress = False):
	"""Play the game as a normal game

	@param fps Specify the updating rate of the game
	@param level Specify the level of the game
	@param record_progress Specify whether to record the game progress or not
	"""
	from .game.arkanoid import Arkanoid

	record_handler = _get_record_handler(record_progress)
	game = Arkanoid(fps, level, record_handler)
	game.game_loop()

def _get_record_handler(record_progress: bool):
	"""Return the handler for record the game progress

	If the `record_progress` is False, return a dummy function.
	"""
	if record_progress:
		from essential.gamedev.recorder import Recorder
		from .game import gamecore
		recorder = Recorder( \
			(gamecore.GAME_OVER_MSG, gamecore.GAME_PASS_MSG), \
			_get_log_dir_path())
		return recorder.record_scene_info
	else:
		return lambda x: None

def _get_log_dir_path():
	import os.path
	dirpath = os.path.dirname(__file__)
	return os.path.join(dirpath, "log")
