def execute(options):
	"""
	Start the game in the selected mode

	An additional game parameter (stored in options.game_params)
	for the game pingpong is the game over score.

	@param options The game options
	"""
	try:
		game_over_score = int(options.game_params[0])
		if game_over_score < 1:
			raise ValueError
	except IndexError:
		print("Gameover score is not specified. Set to 3.")
		game_over_score = 3
	except ValueError:
		print("Invalid game over score. Set to 3.")
		game_over_score = 3

	if options.manual_mode:
		_manual_mode(options.fps, game_over_score, options.record_progress)
	else:
		script_1P, script_2P = get_scripts_name(options.input_script)
		_ml_mode(options.fps, game_over_score, \
			script_1P, script_2P, options.record_progress)

def get_scripts_name(input_scripts):
	"""
	Get the name of scripts for each side.

	@param input_scripts A list of input scripts
	"""
	if len(input_scripts) == 1:
		return input_scripts[0], input_scripts[0]

	return input_scripts[0], input_scripts[1]

def _ml_mode(fps, game_over_score, \
	input_script_1P = "ml_play_template.py", input_script_2P = "ml_play_template.py", \
	record_progress = False):
	"""
	Start the gane in the machine learning mode
	"""
	from multiprocessing import Process, Pipe
	from collections import namedtuple

	CommunicationPipe = namedtuple("CommunicationPipe", ["recv_end", "send_end"])

	instruct_pipe_1P = CommunicationPipe(*Pipe(False))
	instruct_pipe_2P = CommunicationPipe(*Pipe(False))
	scene_info_pipe_1P = CommunicationPipe(*Pipe(False))
	scene_info_pipe_2P = CommunicationPipe(*Pipe(False))
	main_pipe = CommunicationPipe(*Pipe(False))

	game_process = Process(target = _start_game_process, name = "game process", \
		args = (fps, instruct_pipe_1P.recv_end, scene_info_pipe_1P.send_end, \
		instruct_pipe_2P.recv_end, scene_info_pipe_2P.send_end, main_pipe.send_end))
	ml_process_1P = Process(target = _start_ml_process, name = "1P ml process", \
		args = ("1P", input_script_1P, \
		instruct_pipe_1P.send_end, scene_info_pipe_1P.recv_end))
	ml_process_2P = Process(target = _start_ml_process, name = "2P ml process", \
		args = ("2P", input_script_2P, \
		instruct_pipe_2P.send_end, scene_info_pipe_2P.recv_end))

	game_process.start()
	ml_process_1P.start()
	ml_process_2P.start()

	_start_display_process(main_pipe.recv_end, record_progress, game_over_score)

	game_process.terminate()
	ml_process_1P.terminate()
	ml_process_2P.terminate()

def _start_game_process(fps, \
	instruct_pipe_1P, scene_info_pipe_1P, \
	instruct_pipe_2P, scene_info_pipe_2P, main_pipe):
	"""
	Start the process to run the game core

	@param fps The updating rate of the game
	@param instruct_pipe_1P The pipe for receiving the instruction from 1P ml process
	@param scene_info_pipe_1P The pipe for sending the scene info to 1P ml process
	@param instruct_pipe_2P The pipe for receiving the instruction from 2P ml process
	@param scene_info_pipe_2P The pipe for sending the scene info to 2P ml process
	@param main_pipe The pipe for sending scene info to the main process
	"""
	from .game.pingpong_ml import PingPong
	try:
		game = PingPong(instruct_pipe_1P, scene_info_pipe_1P, \
			instruct_pipe_2P, scene_info_pipe_2P, main_pipe)
		game.game_loop(fps)
	except Exception as e:
		import traceback
		from essential.exception import ExceptionMessage
		exc_msg = ExceptionMessage("game", traceback.format_exc())
		main_pipe.send((exc_msg, None))

def _start_ml_process(side, target_script, instruct_pipe, scene_info_pipe):
	"""
	Start the process to execute the user script

	@param side The side of the player. Should be either "1P" or "2P"
	@param target_script The name of the script to be used.
	       Note that the script must have function `ml_loop()` and
	       be placed in the "ml" directory of the game.
	@param instruct_pipe The pipe for sending the instruction to the game process
	@param scene_info_pipe The pipe for receiving the scene info from the game process
	"""
	# Initialize the pipe defined in the communication.py
	from . import communication as comm
	comm._instruct_pipe = instruct_pipe
	comm._scene_info_pipe = scene_info_pipe

	try:
		script_name = target_script.split('.')[0]

		import importlib
		ml = importlib.import_module(".ml.{}".format(script_name), __package__)
		ml.ml_loop(side)
	except Exception as e:
		import traceback
		from essential.exception import ExceptionMessage
		exc_msg = ExceptionMessage("{} ml".format(side), traceback.format_exc())
		comm._instruct_pipe.send(exc_msg)

def _start_display_process(main_pipe, record_progress, game_over_score):
	"""
	Start the process for displaying the game progress

	@param main_pipe The pipe for receiving the scene info from the game process
	@param record_progress Whether to record the game progress or not
	@param game_over_score The score which the game will stop if either of side
	       reaches that score.
	"""
	from .game.pingpong_ml import Screen

	try:
		record_handler = _get_record_handler(record_progress)
		screen = Screen(main_pipe, record_handler)
		exception_msg = screen.draw_loop(game_over_score)
	except Exception as e:
		import traceback
		print(traceback.format_exc())
	else:
		if exception_msg is not None:
			print("Exception occurred in the {} process:" \
				.format(exception_msg.process_name))
			print(exception_msg.exc_msg)

def _manual_mode(fps, game_over_score, record_progress = False):
	"""
	Play the game as a normal game

	@param fps The updating rate of the game
	@param game_over_score The score of game over. The game will be stopped
	       when either of side reaches that score.
	@param record_progress Whether to record the game progress or not
	"""
	from .game.pingpong import PingPong

	record_handler = _get_record_handler(record_progress)
	PingPong().game_loop(fps, game_over_score, record_handler)

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
