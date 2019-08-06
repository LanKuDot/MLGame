import pygame, time
from multiprocessing.connection import Connection

from essential.exception import ExceptionMessage
from essential.game_base import quit_or_esc
from . import gamecore, gameobject
from ..communication import GameInstruction, SceneInfo

class Arkanoid:
	"""The game for the machine learning mode
	"""

	def __init__(self, fps: int, level: int, record_handler = None, \
		one_shot_mode = False):
		self._init_pygame()

		self._fps = fps
		self._record_handler = record_handler
		self._one_shot_mode = one_shot_mode
		self._scene = gamecore.Scene(level, True)

	def _init_pygame(self):
		pygame.display.init()
		pygame.display.set_caption("Arkanoid")
		self._screen = pygame.display.set_mode(gamecore.scene_area_size)
		self._clock = pygame.time.Clock()

	def game_loop(self, instruct_pipe: Connection, scene_info_pipe: Connection):
		"""The main loop of the game in machine learning mode

		This loop is run in a separate process, and it communicates the main process
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

		@param instruct_pipe The receiving-end of the GameInstruction from the ml process
		@param scene_info_pipe The sending-end of the SceneInfo to the ml process
		"""

		def recv_instruction():
			if instruct_pipe.poll():
				instruction = instruct_pipe.recv()

				# Pass the exception to the main process
				if isinstance(instruction, ExceptionMessage):
					raise RuntimeError(instruction)

				if not isinstance(instruction, GameInstruction):
					return GameInstruction(-1, gamecore.ACTION_NONE)

				if instruction.command != gamecore.ACTION_LEFT and \
				   instruction.command != gamecore.ACTION_RIGHT:
					instruction.command = gamecore.ACTION_NONE
			else:
				return GameInstruction(-1, gamecore.ACTION_NONE)

			return instruction

		def wait_ml_process_ready():
			while True:
				ready_instruct = instruct_pipe.recv()

				# Pass the exception to the main process
				if isinstance(ready_instruct, ExceptionMessage):
					raise RuntimeError(ready_instruct)

				if isinstance(ready_instruct, GameInstruction) and \
				   ready_instruct.command == GameInstruction.CMD_READY:
					return

		scene_info = self._scene.fill_scene_info_obj(SceneInfo())
		wait_ml_process_ready()
		# Set the first tick
		self._clock.tick(self._fps)

		while not quit_or_esc():
			self._record_handler(scene_info)
			scene_info_pipe.send(scene_info)

			self._clock.tick(self._fps)

			instruction = recv_instruction()
			game_status = self._scene.update(instruction.command)
			scene_info = self._scene.fill_scene_info_obj(SceneInfo())

			if game_status == gamecore.GAME_OVER_MSG or \
			   game_status == gamecore.GAME_PASS_MSG:
				self._record_handler(scene_info)
				scene_info_pipe.send(scene_info)

				if self._one_shot_mode:
					return

				# TODO Wait the ml process before reset the scene
				self._scene.reset()
				scene_info = self._scene.fill_scene_info_obj(SceneInfo())

			self._screen.fill((0, 0, 0))
			self._scene.draw_gameobjects(self._screen)
			pygame.display.flip()

		pygame.quit()
