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
		print("Invalid game over score. Should be positive integer.")
		return

	if options.manual_mode:
		_manual_mode(options.fps, game_over_score, options.record_progress)
	else:
		print("ML mode unsupported.")

def _manual_mode(fps, game_over_score, reccord_progress = False):
	"""
	Play the game as a normal game

	@param fps The updating rate of the game
	@param game_over_score The score of game over. The game will be stopped
	       when either of side reaches that score.
	@param record_progress Whether to record the game progress or not
	"""
	from .game.pingpong import PingPong

	PingPong().game_loop(fps, game_over_score)
