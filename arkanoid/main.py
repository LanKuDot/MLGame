def ml_mode(fps: int, record_progress: bool, *game_options):
	"""Start the game in the machine learning mode

	Create a game and a machine learning processes, and pipes for communicating.
	The main process is the drawing process, which will draw the scene information
	sent from the game process to the window. After quit from the drawing loop,
	the created processes will be terminated.

	@param fps Specify the fps of the game
	@param record_progress Whether to log the game progress or not
	@param game_options Only one argument is needed. Specify the level of the game
	"""

	from multiprocessing import Process, Pipe
	from .game.arkanoid_ml import Screen

	try:
		level = int(game_options[0])
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

	game_process = Process(target = start_game_process, \
		args = (fps, level, instruct_pipe_r, scene_info_pipe_s, main_pipe_s))
	ml_process = Process(target = start_ml_process, \
		args = (instruct_pipe_s, scene_info_pipe_r))
	screen = Screen()

	ml_process.start()
	game_process.start()

	log_path = None
	if record_progress:
		log_path = __get_log_path()
	
	screen.draw_loop(main_pipe_r, log_path)

	ml_process.terminate()
	game_process.terminate()

def start_game_process(*args):
	"""Start the Arkanoid in the machine learning mode
	"""
	from .game.arkanoid_ml import Arkanoid
	try:
		Arkanoid().game_loop(*args)
	except Exception as e:
		print(e.with_traceback())

def start_ml_process(instruct_pipe, scene_info_pipe):
	"""Start the custom machine learning process

	@param instruct_pipe The sending-end of pipe for the game instruction
	@param scene_info_pipe The receving-end of pipe for the scene information
	"""
	# Initialize the pipe for helper functions in communication.py
	from . import communication as comm
	comm._instruct_pipe = instruct_pipe
	comm._scene_info_pipe = scene_info_pipe

	from .ml import ml_play
	try:
		ml_play.ml_loop()
	except Exception as e:
		print(e.with_traceback())

def manual_mode(fps: int, record_progress: bool, *game_options):
	"""Play the game as a normal game

	@param fps Specify the fps of the game
	@param record_progress Whether to log the game progress or not
	@param game_options Only one argument is needed. Specify the level of the game
	"""
	from .game.arkanoid import Arkanoid
	
	try:
		level = int(game_options[0])
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
