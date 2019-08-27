from essential.gameconfig import GameConfig

def ml_mode(config: GameConfig):
	"""
	Start the game in the machine learning mode
	"""
	game_over_score = _get_game_over_score(config.game_params, config.one_shot_mode)
	module_1P, module_2P = _get_ml_modules(config.input_modules)
	to_transition = True if config.transition_channel else False

	from essential.process import ProcessManager

	process_manager = ProcessManager()
	process_manager.set_game_process(_start_game_process, \
		args = (config.fps, game_over_score, \
		config.record_progress, to_transition))
	process_manager.add_ml_process(module_1P, "ml_1P", args = ("1P", ))
	process_manager.add_ml_process(module_2P, "ml_2P", args = ("2P", ))

	if to_transition:
		process_manager.set_transition_process(*config.transition_channel)

	process_manager.start()

def _get_ml_modules(input_modules):
	"""
	Get the modules for 1P and 2P
	
	If only 1 input module specified, 1P and 2P use the same module.
	"""
	if len(input_modules) == 1:
		return input_modules[0], input_modules[0]

	return input_modules[0], input_modules[1]

def _start_game_process(fps, game_over_score, record_progress, to_transition):
	"""
	Start the process to run the game core

	@param fps The updating rate of the game
	"""
	from .game.pingpong_ml import PingPong

	record_handler = _get_record_handler(record_progress)
	game = PingPong(fps, game_over_score, record_handler, to_transition)
	game.game_loop()

def manual_mode(config: GameConfig):
	"""
	Play the game as a normal game
	"""
	from .game.pingpong import PingPong

	game_over_score = _get_game_over_score(config.game_params, config.one_shot_mode)
	record_handler = _get_record_handler(config.record_progress)

	game = PingPong(config.fps, game_over_score, record_handler)
	game.game_loop()

def _get_game_over_score(game_params, one_shot_mode):
	"""
	Get game over score from the parameter
	"""
	if one_shot_mode:
		print("One shot mode is on. Set game-over score to 1.")
		return 1

	try:
		game_over_score = int(game_params[0])
		if game_over_score < 1:
			raise ValueError
	except IndexError:
		print("Game-over score is not specified. Set to 3.")
		game_over_score = 3
	except ValueError:
		print("Invalid game-over score. Set to 3.")
		game_over_score = 3

	return game_over_score

def _get_record_handler(record_progress: bool):
	"""
	Get the record handler for record the game progress

	If the `record_progress` is False, it will return a dummy function
	"""
	if record_progress:
		import os.path
		log_dir_path = os.path.join(os.path.dirname(__file__), "log")

		from essential.recorder import Recorder
		from .game import gamecore
		recorder = Recorder( \
			(gamecore.GameStatus.GAME_1P_WIN, gamecore.GameStatus.GAME_2P_WIN), \
			log_dir_path)
		return recorder.record_scene_info
	else:
		return lambda x: None
