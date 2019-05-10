def execute(options, *game_params):
	"""
	Start the game in the selected mode

	@param options The game options
	@param game_params Additional game parameters. There are two paramters is used,
	       one is the score of game over,
	       the other is the manual side in the ml mode [Optional].
	"""
	try:
		game_over_score = int(game_params[0])
		if game_over_score < 1:
			raise ValueError

		game_params[1].upper()
		if game_params[1] == "1P" or game_params[1] == "2P":
			manual_side = game_params[1]
		else:
			raise IndexError
	except IndexError:
		if len(game_params) == 0:
			print("The game over score is not specified.")
			print("Usage: pingpong <game_over_score> [manual_side]")
			return
		else:
			print("The manual side is not specified or is invalid. Set to None.")
			manual_side = None
	except ValueError:
		print("Invalid game over score. Should be a positive integer.")
		return

	if options.manual_mode:
		_manual_mode(options.fps, game_over_score, options.record_progress)
	else:
		_ml_mode(options.fps, game_over_score)

def _ml_mode(fps, game_over_score, \
	input_script_1P = "ml_play_1P.py", input_script_2P = "ml_play_2P.py", \
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
		ml.ml_loop()
	except Exception as e:
		import traceback
		from essential.exception import ExceptionMessage
		exc_msg = ExceptionMessage("{} ml".format(side), traceback.format_exc())
		comm._instruct_pipe.send(exc_msg)

def _start_display_process(main_pipe, record_process, game_over_score):
	"""
	Start the process for displaying the game progress

	@param main_pipe The pipe for receiving the scene info from the game process
	@param record_process Whether to record the game progress or not
	@param game_over_score The score which the game will stop if either of side
	       reaches that score.
	"""
	from .game.pingpong_ml import Screen

	try:
		screen = Screen(main_pipe)
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

	PingPong().game_loop(fps, game_over_score)
