def execute(options, *game_params):
	"""Start the game in the selected mode

	@param options The game options specified in the command line
	@param game_params Additional game parameter. Only one parameter is needed
	       for specifying the level of the game.
	"""
	try:
		level = int(game_params[0])
		if level < 1:
			raise ValueError
	except IndexError:
		print("Level is not specified. Set to 1.")
		level = 1
	except ValueError:
		print("Invalid level value. Set to 1.")
		level = 1

	if options.manual_mode:
		_manual_mode(options.fps, level, options.record_progress)
	else:
		_ml_mode(options.fps, level, options.input_script, \
			options.record_progress, options.one_shot_mode)

def _ml_mode(fps, level, input_script = "ml_play.py", \
	record_progress = False, one_shot_mode = False):
	"""Start the game in the machine learning mode

	Create a game and a machine learning processes, and pipes for communicating.
	The main process is the drawing process, which will draw the game progress
	accroding to the information sent from the game process.

	After quit from the drawing loop,
	the created processeswill be terminated.

	@param fps Specify the updating rate of the game
	@param level Specify the level of the game
	@param input_script Specify the script for the ml process
	@param record_progress Specify whether to record the game progress or not
	@param one_shot_mode Specify whether to run the game only once or not
	"""

	from multiprocessing import Process, Pipe

	instruct_pipe_r, instruct_pipe_s = Pipe(False)
	scene_info_pipe_r, scene_info_pipe_s = Pipe(False)
	main_pipe_r, main_pipe_s = Pipe(False)

	game_process = Process(target = _start_game_process, name = "game process", \
		args = (fps, level, instruct_pipe_r, scene_info_pipe_s, main_pipe_s))
	ml_process = Process(target = _start_ml_process, name = "ml process", \
		args = (input_script, instruct_pipe_s, scene_info_pipe_r))

	ml_process.start()
	game_process.start()

	_start_display_process(main_pipe_r, record_progress, one_shot_mode)

	ml_process.terminate()
	game_process.terminate()

def _start_game_process(fps, level, \
	instruct_pipe, scene_info_pipe, main_pipe):
	"""Start the game process

	@param fps Specify the updating rate of the game
	@param level Specify the level of the game
	@param instruct_pipe The pipe for receving the instruction from the ml process
	@param scene_info_pipe The pipe for sending the scene info to the ml process
	@param main_pipe The pipe for sending the scene info to the main process
	"""
	from .game.arkanoid_ml import Arkanoid
	try:
		Arkanoid().game_loop(fps, level, instruct_pipe, scene_info_pipe, main_pipe)
	except Exception as e:
		import traceback
		from essential.exception import ExceptionMessage
		exc_msg = ExceptionMessage("game", traceback.format_exc())
		main_pipe.send((exc_msg, None))

def _start_ml_process(target_script, instruct_pipe, scene_info_pipe):
	"""Start the custom machine learning process

	@param target_script Specify the name of the script to be used.
	       The Script must have function `ml_loop()` and be put in the "ml"
	       directory of the game.
	@param instruct_pipe The sending-end of pipe for the game instruction
	@param scene_info_pipe The receving-end of pipe for the scene information
	"""
	# Initialize the pipe for helper functions in communication.py
	from . import communication as comm
	comm._instruct_pipe = instruct_pipe
	comm._scene_info_pipe = scene_info_pipe

	try:
		script_name = target_script.split('.')[0]

		import importlib
		ml = importlib.import_module(".ml.{}".format(script_name), __package__)
		ml.ml_loop()
	except Exception as e:
		import traceback
		from essential.exception import ExceptionMessage
		exc_msg = ExceptionMessage("ml", traceback.format_exc())
		comm._instruct_pipe.send(exc_msg)

def _start_display_process(main_pipe, record_progress, one_shot_mode):
	"""Start the process for displaying the game progress

	@param main_pipe The receving-end of pipe for the scene information
	@param record_progress Whether to record the game progress or not
	@param one_shot_mode Whether to execute the game for only once or not
	"""
	from .game.arkanoid_ml import Screen
	
	screen = Screen()
	record_handler = _get_record_handler(record_progress)
	exception_msg = screen.draw_loop(main_pipe, record_handler, one_shot_mode)

	if exception_msg is not None:
		print("Exception occurred in the {} process:".format(exception_msg.process_name))
		print(exception_msg.exc_msg)

def _manual_mode(fps, level, record_progress = False):
	"""Play the game as a normal game

	@param fps Specify the updating rate of the game
	@param level Specify the level of the game
	@param record_progress Specify whether to record the game progress or not
	"""
	from .game.arkanoid import Arkanoid

	record_handler = _get_record_handler(record_progress)
	Arkanoid().game_loop(fps, level, record_handler)

def _get_record_handler(record_progress: bool):
	"""Return the handler for record the game progress

	If the `record_progress` is False, return a dummy function.
	"""
	if record_progress:
		from essential.recorder import Recorder
		recorder = Recorder(_get_log_dir_path())
		return recorder.record_scene_info
	else:
		return lambda x: None

def _get_log_dir_path():
	import os.path
	dirpath = os.path.dirname(__file__)
	return os.path.join(dirpath, "log")
