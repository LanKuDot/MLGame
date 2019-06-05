import pygame
from multiprocessing.connection import Connection
from collections import namedtuple

from essential.exception import ExceptionMessage
from essential.online import MessageServer

from . import gamecore, gameobject
from .. import communication as comm
from ..communication import SceneInfo, GameInstruction

class PingPong:
	"""
	The game core for the maching learning mode
	"""
	def __init__(self, \
		instruct_pipe_1P: Connection, scene_info_pipe_1P: Connection, \
		instruct_pipe_2P: Connection, scene_info_pipe_2P: Connection, \
		main_pipe: Connection):
		"""
		Constructor

		@param instruct_pipe_1P The pipe for receiving GameInstruction from 1P player
		@param scene_info_pipe_1P The pipe for sending SceneInfo to 1P player
		@param instruct_pipe_2P The pipe for receiving GameInstruction from 2P player
		@param scene_info_pipe_2P The pipe for sending SceneInfo to 2P player
		@param main_pipe The pipe for sending modified SceneInfo to the main process
		"""
		CommunicationPipe = namedtuple("CommunicationPipe", ("recv_end", "send_end"))
		self._ml_pipes = {
			"1P": CommunicationPipe(instruct_pipe_1P, scene_info_pipe_1P),
			"2P": CommunicationPipe(instruct_pipe_2P, scene_info_pipe_2P),
		}
		self._main_pipe = main_pipe

		self._init_pygame()

	def _init_pygame(self):
		self._clock = pygame.time.Clock()

	def game_loop(self, fps: int):
		"""
		The main loop of the game execution

		@param fps The updating rate of the game
		"""
		scene = gamecore.Scene(False)
		scene_info = scene.fill_scene_info_obj(SceneInfo())

		self._wait_ml_process_ready()

		# Set the first tick
		self._clock.tick_busy_loop(fps)

		while True:
			# Send the scene info to the ml processes and wait for instructions
			self._send_scene_info(scene_info)

			self._clock.tick_busy_loop(fps)

			instruction_1P, instruction_2P = self._recv_instruction()
			self._main_pipe.send((scene_info, (instruction_1P, instruction_2P)))

			# Update the scene
			game_status = scene.update( \
				gamecore.PlatformMoveAction[instruction_1P.command.value], \
				gamecore.PlatformMoveAction[instruction_2P.command.value])
			scene_info = scene.fill_scene_info_obj(SceneInfo())

			# If either of two sides wins, reset the scene and wait for ml processes
			# getting ready for the next round
			if game_status == gamecore.GameStatus.GAME_1P_WIN or \
			   game_status == gamecore.GameStatus.GAME_2P_WIN:
				self._send_scene_info(scene_info)
				self._main_pipe.send((scene_info, None))

				scene.reset()
				scene_info = scene.fill_scene_info_obj(SceneInfo())
				# Wait for ml processes doing their reseting jobs
				self._wait_ml_process_ready()

	def _send_scene_info(self, scene_info: SceneInfo):
		"""
		Send the SceneInfo to both ml process

		@param scene_info The scene info to be sent
		"""
		self._ml_pipes["1P"].send_end.send(scene_info)
		self._ml_pipes["2P"].send_end.send(scene_info)

	def _recv_instruction(self):
		"""
		Get the GameInstruction from both ml processes

		This function is non-blocking. If there is nothing available in the pipe,
		it will return a dummy GameInstruction.
		"""
		def recv_instruction_from_pipe(target_pipe: Connection):
			if target_pipe.poll():
				instruction = target_pipe.recv()

				# Pass the exception to the main process
				if isinstance(instruction, ExceptionMessage):
					self._main_pipe.send((instruction, None))

				# Invalid instruction object
				if not isinstance(instruction, GameInstruction):
					return GameInstruction(-1, comm.PlatformAction.NONE)

				# Invalid PlatformAction instruction
				if instruction.command != comm.PlatformAction.MOVE_LEFT and \
				   instruction.command != comm.PlatformAction.MOVE_RIGHT:
					instruction.command = comm.PlatformAction.NONE

				return instruction
			else:
				return GameInstruction(-1, comm.PlatformAction.NONE)

		instruction_1P = recv_instruction_from_pipe(self._ml_pipes["1P"].recv_end)
		instruction_2P = recv_instruction_from_pipe(self._ml_pipes["2P"].recv_end)

		return instruction_1P, instruction_2P

	def _wait_ml_process_ready(self):
		"""
		Wait until receiving the ready command from both ml processes
		"""
		def wait_ready_command(target_pipe):
			while True:
				ready_instruct = target_pipe.recv()

				# Pass the exception to the main process and exit the waiting loop
				if isinstance(ready_instruct, ExceptionMessage):
					self._main_pipe.send((ready_instruct, None))
					return

				if isinstance(ready_instruct, GameInstruction) and \
				   ready_instruct.command == comm.PlatformAction.READY:
					return

		wait_ready_command(self._ml_pipes["1P"].recv_end)
		wait_ready_command(self._ml_pipes["2P"].recv_end)

class Screen:
	"""
	The drawing process for displaying the status of the game
	"""
	def __init__(self, scene_info_pipe: Connection, record_handler = lambda x: None):
		self._scene_info_pipe = scene_info_pipe
		self._record_handler = record_handler
		self._delayed_frame = [0, 0]	# 1P, 2P

		self._init_pygame()
		self._create_surface()

	def _init_pygame(self):
		pygame.display.init()
		self._screen = pygame.display.set_mode(gamecore.display_area_size)
		pygame.display.set_caption("PingPong")

		pygame.font.init()
		self._font = pygame.font.Font(None, 22)
		self._font_pos_1P = (1, 4)
		self._font_pos_2P = (1, gamecore.display_area_size[1] - 21)
		self._font_pos_speed = (gamecore.display_area_size[0] - 75, \
			gamecore.display_area_size[1] - 21)

	def _create_surface(self):
		ball_sprite = gameobject.Ball((0, 0))
		ball_sprite.create_surface()
		platform_1P_sprite = gameobject.Platform((0, 0), (0, 0))
		platform_1P_sprite.create_surface("1P", gamecore.color_1P)
		platform_2P_sprite = gameobject.Platform((0, 0), (0, 0))
		platform_2P_sprite.create_surface("2P", gamecore.color_2P)

		self._ball_surface = ball_sprite.image
		self._platform_1P_surface = platform_1P_sprite.image
		self._platform_2P_surface = platform_2P_sprite.image

	def _check_going(self):
		"""
		Check if the game window is closed or ESC key is pressed.
		"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT or \
				(event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				return False
		return True

	def draw_loop(self, game_over_score: int):
		"""
		Receive the SceneInfo from the game process and draw on the window

		It will count the score accroding to the SceneInfo received.
		If either of side reaches `game_over_score`, exit the loop.
		"""
		score = [0, 0]	# 1P, 2P

		while self._check_going():
			scene_info, instructions = self._scene_info_pipe.recv()
			# If receive an exception, pass the exception and quit the game.
			if isinstance(scene_info, ExceptionMessage):
				return scene_info

			if instructions:
				scene_info.command_1P = instructions[0].command.value
				scene_info.command_2P = instructions[1].command.value
				self._check_delayed_frame(scene_info.frame, \
					instructions[0].frame, instructions[1].frame)
			self._record_handler(scene_info)

			# If either of two sides wins, print the game status and update the score
			if scene_info.status == gamecore.GameStatus.GAME_1P_WIN or \
			   scene_info.status == gamecore.GameStatus.GAME_2P_WIN:
				print("Frame: {}, Status: {}" \
					.format(scene_info.frame, scene_info.status))
				print("-----")

				# Reset delayed frame
				self._delayed_frame = [0, 0]

				# Update the score
				if scene_info.status == gamecore.GameStatus.GAME_1P_WIN:
					score[0] += 1
				else:
					score[1] += 1
				if score[0] == game_over_score or \
				   score[1] == game_over_score:
					break

			self._screen.fill((0, 0, 0))
			self._screen.blit(self._ball_surface, scene_info.ball)
			self._screen.blit(self._platform_1P_surface, scene_info.platform_1P)
			self._screen.blit(self._platform_2P_surface, scene_info.platform_2P)

			font_surface_1P = self._font.render( \
				"1P score: {}".format(score[0]), True, gamecore.color_1P)
			font_surface_2P = self._font.render( \
				"2P score: {}".format(score[1]), True, gamecore.color_2P)
			font_surface_speed = self._font.render( \
				"Speed: {}".format(scene_info.ball_speed), True, (255, 255, 255))
			self._screen.blit(font_surface_1P, self._font_pos_1P)
			self._screen.blit(font_surface_2P, self._font_pos_2P)
			self._screen.blit(font_surface_speed, self._font_pos_speed)

			pygame.display.flip()

		if score[0] > score[1]:
			print("1P wins!")
		else:
			print("2P wins!")
		print("Final score: {}-{}".format(score[0], score[1]))

	def _check_delayed_frame(self, scene_frame, command_frame_1P, command_frame_2P):
		"""
		Check if the received instruction is delayed. If yes, output the message.
		"""
		if scene_frame - command_frame_1P == self._delayed_frame[0] + 1:
			self._delayed_frame[0] += 1
			print("1P delayed {} frame(s)".format(self._delayed_frame[0]))

		if scene_frame - command_frame_2P == self._delayed_frame[1] + 1:
			self._delayed_frame[1] += 1
			print("2P delayed {} frame(s)".format(self._delayed_frame[1]))

class TransitionServer:
	"""
	Pass the scene info received to the message server
	"""
	def __init__(self, server_ip, server_port, channel_name):
		"""
		Constructor

		@param server_ip The ip of the remote server
		@param server_port The port of the remote server
		@param channel_name The name of the channel of remote server for sending
		       the message
		"""
		self._message_server = MessageServer(server_ip, server_port, channel_name)
		self._delay_frame = [0, 0]	# 1P, 2P
		self._score = [0, 0]	# 1P, 2P

	def transition_loop(self, scene_info_pipe: Connection, game_over_score, \
		record_handler):
		"""
		Receive the SceneInfo from the game process and pass to the message server

		@param scene_info_pipe The pipe for receiving the SceneInfo
		@param game_over_score The score that when either of both sides gets that score,
		       the game will be stopped.
		@param record_handler The handler for recording the game progress
		"""
		while True:
			scene_info, instructions = scene_info_pipe.recv()
			if isinstance(scene_info, ExceptionMessage):
				self._send_exception(scene_info)
				return

			if instructions:
				if scene_info.frame - instructions[0].frame == self._delay_frame[0] + 1:
					self._delay_frame[0] += 1
				if scene_info.frame - instructions[1].frame == self._delay_frame[1] + 1:
					self._delay_frame[1] += 1

			self._send_scene_info(scene_info)
			record_handler(scene_info)

			if scene_info.status == gamecore.GameStatus.GAME_1P_WIN or \
			   scene_info.status == gamecore.GameStatus.GAME_2P_WIN:
				if scene_info.status == gamecore.GameStatus.GAME_1P_WIN:
					self._score[0] += 1
				else:
					self._score[1] += 1

				self._delay_frame = [0, 0]

				if self._score[0] == game_over_score or \
				   self._score[1] == game_over_score:
					self._send_game_result()
					return

	def _send_scene_info(self, scene_info: SceneInfo):
		"""
		Send the scene info to the message server
		"""
		scene_info_dict = {
			"frame": scene_info.frame,
			"delay_frame": self._delay_frame,
			"status": scene_info.status,
			"ball": scene_info.ball,
			"ball_speed": scene_info.ball_speed,
			"platform_1P": scene_info.platform_1P,
			"platform_2P": scene_info.platform_2P,
		}

		message_object = {
			"type": "game_progress",
			"scene_info": scene_info_dict,
		}
		self._message_server.send(message_object)

	def _send_game_result(self):
		"""
		Send the game result fo the message server
		"""
		if self._score[0] > self._score[1]:
			status = gamecore.GameStatus.GAME_1P_WIN.value
		else:
			status = gamecore.GameStatus.GAME_2P_WIN.value

		game_result_dict = {
			"status": status,
			"score": self._score,
		}

		message_object = {
			"type": "game_result",
			"result": game_result_dict,
		}
		self._message_server.send(message_object)

	def _send_exception(self, exception_msg: ExceptionMessage):
		"""
		Send the exception message to the message server
		"""
		message_object = {
			"type": "game_error",
			"message": "Error occurred in {} process.\n{}" \
				.format(exception_msg.process_name, exception_msg.exc_msg),
		}
		self._message_server.send(message_object)
