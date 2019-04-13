import pygame, time
from multiprocessing.connection import Connection

from essential.game_base import GameABC
from essential.exception import ExceptionMessage
from essential.online.transition import RedisTransition

from . import gamecore, gameobject
from ..communication import GameInstruction, SceneInfo

class Arkanoid(GameABC):
	"""The game for the machine learning mode
	"""

	def __init__(self):
		self._init_pygame()

	def _init_pygame(self):
		pygame.init()
		pygame.mixer.quit()
		self._clock = pygame.time.Clock()

	def game_loop(self, fps: int, level: int, \
		instruct_pipe: Connection, scene_info_pipe: Connection, main_pipe: Connection):
		"""The main loop of the game in machine learning mode

		This loop is run in a seperate process, and it communicates the main process
		and the machine learning process with pipes.
		The execution order in the loops:
		1. Send the SceneInfo to the machine learning process and the main process.
		2. Wait for the keyframe (During this period, machine learning process can
		   process the SceneInfo and generate the GameInstruction.)
		3. Check if there has a GameInstruction to receive. If it has, receive the
		   instruction. Otherwise, generate a dummy one.
		4. Pass the GameInstruction to the game and update the scene (and frame no.)
		5. If the game is over or passed, send the SceneInfo containing the
		   game status to the both processes, and reset the game.
		6. Back to 1.

		@param fps Specify the updating rate of the game
		@param level Specify the level of the game
		@param instruct_pipe The receving-end of the GameInstruction from the ml process
		@param scene_info_pipe The sending-end of the SceneInfo to the ml process
		@param main_pipe The sending-end of the SceneInfo to the main process
		"""

		def recv_instruction():
			if instruct_pipe.poll():
				instruction = instruct_pipe.recv()

				# Pass the exception to the main process
				if isinstance(instruction, ExceptionMessage):
					main_pipe.send((instruction, None))

				if not isinstance(instruction, GameInstruction):
					return GameInstruction(-1, gamecore.ACTION_NONE)

				if instruction.command != gamecore.ACTION_LEFT and \
				   instruction.command != gamecore.ACTION_RIGHT:
					instruction.command = gamecore.ACTION_NONE
			else:
				return GameInstruction(-1, gamecore.ACTION_NONE)

			return instruction

		scene = gamecore.Scene(level, False)
		scene_info = scene.fill_scene_info_obj(SceneInfo())
		# Wait for ready instruction
		instruct_pipe.recv()
		self._clock.tick(fps)

		while True:
			scene_info_pipe.send(scene_info)

			self._clock.tick(fps)

			instruction = recv_instruction()
			main_pipe.send((scene_info, instruction))

			game_status = scene.update(instruction.command)
			scene_info = scene.fill_scene_info_obj(SceneInfo())

			if game_status == gamecore.GAME_OVER_MSG or \
			   game_status == gamecore.GAME_PASS_MSG:
				scene_info_pipe.send(scene_info)
				main_pipe.send((scene_info, None))

				# TODO Wait the ml process before reset the scene
				scene.reset()
				scene_info = scene.fill_scene_info_obj(SceneInfo())

class Screen:
	"""The drawing process for the game in the machine leraning mode
	"""

	def __init__(self):
		self._init_pygame()
		self._create_surface()

	def _init_pygame(self):
		pygame.init()
		pygame.mixer.quit()
		self._screen = pygame.display.set_mode(gamecore.display_area_size)
		pygame.display.set_caption("Arkanoid")
		self._font = pygame.font.Font(None, 22)
		self._font_pos = (1, gamecore.display_area_size[1] - 21)

	def _create_surface(self):
		brick_sprite = gameobject.Brick((0, 0))
		brick_sprite.create_surface()
		platform_sprite = gameobject.Platform((0, 0), 0)
		platform_sprite.create_surface()
		ball_sprite = gameobject.Ball((0, 0), 0)
		ball_sprite.create_surface()

		self._brick_surface = brick_sprite.image
		self._platform_surface = platform_sprite.image
		self._ball_surface = ball_sprite.image

	def draw_loop(self, scene_info_pipe: Connection, record_handler = None, \
		one_shot_mode: bool = False):
		"""Receive the SceneInfo from the game process and draw on the window

		Use ESC key or click X in the window bar to exit the drawing loop.

		@param scene_info_pipe The receiving-end of the SceneInfo from the game process
		@param record_handler Specify the handler for record the game progress
		@param one_shot_mode Run the draw loop in one_shot mode. The draw loop will
		       be exited once the game is over or is passed.
		@return None or ExceptionMessage if it receives the exception from the main pipe
		"""

		def check_going():
			for event in pygame.event.get():
				if event.type == pygame.QUIT or \
				  (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					return False
			return True

		while check_going():
			scene_info, instruction = scene_info_pipe.recv()
			# If receive an exception, pass the exception and quit the game.
			if isinstance(scene_info, ExceptionMessage):
				return scene_info

			record_handler(scene_info)
			if scene_info.status == SceneInfo.STATUS_GAME_OVER or \
			   scene_info.status == SceneInfo.STATUS_GAME_PASS:
				print("Frame: {} {}".format(scene_info.frame, scene_info.status))
				print("-----")
				if one_shot_mode:
					return
			else:
				print("Frame: {}/{} Cmd: {}" \
					.format(scene_info.frame, instruction.frame, instruction.command))

			self._screen.fill((0, 0, 0))
			self._screen.blit(self._ball_surface, scene_info.ball)
			self._screen.blit(self._platform_surface, scene_info.platform)
			for brick in scene_info.bricks:
				self._screen.blit(self._brick_surface, brick)

			font_surface = self._font.render( \
				"Frame: {}".format(scene_info.frame), True, (255, 255, 255))
			self._screen.blit(font_surface, self._font_pos)

			pygame.display.flip()

		pygame.quit()

class TransitionServer:
	"""Pass the scene info received to the message server
	"""
	def __init__(self, channel_name):
		"""Contstructor

		@param channel_name The name of the channel of remote server for sending
		       the message.
		"""
		self._message_server = RedisTransition(channel_name)

	def transition_loop(self, scene_info_pipe: Connection, log_dir: str = None):
		"""Recevie the SceneInfo from the game process and pass to the message server

		Transition loop always runs in one shot mode, therefore,
		it will be exited after the game is over or is passed.
		"""
		while True:
			scene_info = scene_info_pipe.recv()
			if isinstance(scene_info, ExceptionMessage):
				self._send_exception(scene_info)
				return

			self._send_scene_info(scene_info)
			if scene_info.status == SceneInfo.STATUS_GAME_OVER or \
			   scene_info.status == SceneInfo.STATUS_GAME_PASS:
				self._send_game_result(scene_info)
				return

	def _send_scene_info(self, scene_info: SceneInfo):
		"""Send the scene info to the message server
		"""
		scene_info_dict = {
			"frame": scene_info.frame,
			"status": scene_info.status,
			"ball": scene_info.ball,
			"platform": scene_info.platform,
			"bricks": scene_info.bricks,
		}

		message_object = {
			"type": "game_progress",
			"scene_info": scene_info_dict
		}
		self._message_server.send(message_object)

	def _send_game_result(self, scene_info: SceneInfo):
		"""Send the game result to the message server
		"""
		game_result_dict = {
			"status": scene_info.status,
			"frame_used": scene_info.frame,
			"bricks_remain": len(scene_info.bricks),
		}

		message_object = {
			"type": "game_result",
			"result": game_result_dict,
		}
		self._message_server.send(message_object)

	def _send_exception(self, exception_msg: ExceptionMessage):
		"""Send the exception message to the message server
		"""
		message_object = {
			"type": "game_error",
			"error_message": "Error occuered in {} process.\n{}" \
				.format(exception_msg.process_name, exception_msg.exc_msg),
		}
		self._message_server.send(message_object)
