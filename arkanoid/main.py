def ml_mode(options, *game_params):
	"""Start the game in the machine learning mode

	Create a game and a machine learning processes, and pipes for communicating.
	The main process is the drawing process, which will draw the scene information
	sent from the game process to the window. After quit from the drawing loop,
	the created processes will be terminated.

	@param options Specify the game settings
	@param game_params Only one parameter is needed. Specify the level of the game
	"""

	from multiprocessing import Process, Pipe

	fps = options.fps
	record_progress = options.record
	one_shot_mode = options.one_shot

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

	instruct_pipe_r, instruct_pipe_s = Pipe(False)
	scene_info_pipe_r, scene_info_pipe_s = Pipe(False)
	main_pipe_r, main_pipe_s = Pipe(False)

	game_process = Process(target = start_game_process, name = "game process", \
		args = (fps, level, instruct_pipe_r, scene_info_pipe_s, main_pipe_s))
	ml_process = Process(target = start_ml_process, name = "ml process", \
		args = (options.input_script, instruct_pipe_s, scene_info_pipe_r))

	ml_process.start()
	game_process.start()

	start_display_process(main_pipe_r, record_progress, one_shot_mode)

	ml_process.terminate()
	game_process.terminate()

def start_game_process(*args):
	"""Start the Arkanoid in the machine learning mode

	@param args The arguments to be passed to the game loop
	"""
	from .game.arkanoid_ml import Arkanoid
	try:
		Arkanoid().game_loop(*args)
	except Exception as e:
		import traceback
		from essential.exception import ExceptionMessage
		exc_msg = ExceptionMessage("game", traceback.format_exc())
		main_pipe = args[-1]
		main_pipe.send(exc_msg)

def start_ml_process(target_script, instruct_pipe, scene_info_pipe):
	"""Start the custom machine learning process

	@param target_script Specify the name of the script to be used
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

def start_display_process(main_pipe, record_progress, one_shot_mode):
	"""Start the process for displaying the game progress

	@param main_pipe The receving-end of pipe for the scene information
	@param record_progress Whether to record the game progress or not
	@param one_shot_mode Whether to execute the game for only once or not
	"""
	from .game.arkanoid_ml import Screen
	
	log_path = None
	if record_progress:
		log_path = __get_log_path()

	screen = Screen()
	exception_msg = screen.draw_loop(main_pipe, log_path, one_shot_mode)

	if exception_msg is not None:
		print("Exception occurred in the {} process:".format(exception_msg.process_name))
		print(exception_msg.exc_msg)

def manual_mode(options, *game_params):
	"""Play the game as a normal game

	@param options Specify the game settings
	@param game_params Only one parameter is needed. Specify the level of the game
	"""
	from .game.arkanoid import Arkanoid

	fps = options.fps
	record_progress = options.record

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

	log_path = None
	if record_progress:
		log_path = __get_log_path()

	Arkanoid().game_loop(fps, level, log_path)

def __get_log_path():
	import os.path
	dirpath = os.path.dirname(__file__)
	return os.path.join(dirpath, "log")
