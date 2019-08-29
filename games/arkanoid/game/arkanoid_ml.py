import pygame, time

from mlgame.gamedev.generic import quit_or_esc
from mlgame.gamedev.recorder import get_record_handler
from mlgame.communication import game as comm
from mlgame.communication.game import CommandReceiver

from . import gamecore
from .gamecore import GameStatus, PlatformAction
from ..communication import GameInstruction, SceneInfo
from ..main import get_log_dir

class Arkanoid:
	"""The game for the machine learning mode
	"""

	def __init__(self, fps: int, level: int, \
		record_progress: bool, one_shot_mode: bool, to_transition: bool):
		self._ml_name = "ml"
		self._ml_execute_time = 1.0 / fps
		self._frame_delayed = 0
		self._instruct_receiver = CommandReceiver( \
			GameInstruction, { "command": \
				[PlatformAction.MOVE_LEFT, PlatformAction.MOVE_RIGHT, PlatformAction.NONE], \
			}, GameInstruction(-1, PlatformAction.NONE))

		self._record_handler = get_record_handler(record_progress, { \
				"status": (GameStatus.GAME_OVER, GameStatus.GAME_PASS) \
			}, get_log_dir())
		self._to_transition = to_transition
		self._one_shot_mode = one_shot_mode

		if not self._to_transition:
			self._init_display()
			self._scene = gamecore.Scene(level, True)
		else:
			self._scene = gamecore.Scene(level, False)
			self._transition_server = TransitionServer()

	def _init_display(self):
		pygame.display.init()
		pygame.display.set_caption("Arkanoid")
		self._screen = pygame.display.set_mode(gamecore.scene_area_size)

	def game_loop(self):
		"""The main loop of the game in machine learning mode

		The execution order in the loop:
		1. Send the SceneInfo to the machine learning process.
		2. Wait for the key frame (During this period, machine learning process can
		   process the SceneInfo and generate the GameInstruction.)
		3. Check if there has a GameInstruction to receive. If it has, receive the
		   instruction. Otherwise, generate a dummy one.
		4. Pass the GameInstruction to the game and update the scene (and frame no.)
		5. If the game is over or passed, send the SceneInfo containing the
		   game status to the machine learning process, and reset the game.
		6. Back to 1.
		"""

		if self._to_transition:
			self._transition_server._send_game_info()
			keep_going = lambda : True
		else:
			keep_going = lambda : not quit_or_esc()

		comm.wait_ml_ready(self._ml_name)

		while keep_going():
			scene_info = self._scene.fill_scene_info_obj(SceneInfo())
			self._record_handler(scene_info)

			instruction = self._make_ml_execute(scene_info)
			game_status = self._scene.update(instruction.command)

			if not self._to_transition:
				self._draw_scene()
			else:
				self._transition_server._send_scene_info(scene_info, self._frame_delayed)

			if game_status == GameStatus.GAME_OVER or \
			   game_status == GameStatus.GAME_PASS:
				scene_info = self._scene.fill_scene_info_obj(SceneInfo())
				self._record_handler(scene_info)
				comm.send_to_ml(scene_info, self._ml_name)

				if self._to_transition:
					self._transition_server._send_scene_info(scene_info, self._frame_delayed)
					self._transition_server._send_game_result(scene_info, self._frame_delayed)

				if self._one_shot_mode:
					return

				# TODO Wait the ml process before reset the scene
				self._scene.reset()

		pygame.quit()

	def _make_ml_execute(self, scene_info):
		"""Send the scene_info to the ml process and wait for the instruction
		"""
		comm.send_to_ml(scene_info, self._ml_name)
		time.sleep(self._ml_execute_time)
		instruction = self._instruct_receiver.recv(self._ml_name)

		if instruction.frame != -1 and \
		   scene_info.frame - instruction.frame > self._frame_delayed:
			self._frame_delayed = scene_info.frame - instruction.frame
			print("Delayed {} frame(s)".format(self._frame_delayed))

		return instruction

	def _draw_scene(self):
		"""Draw the scene to the display
		"""
		self._screen.fill((0, 0, 0))
		self._scene.draw_gameobjects(self._screen)
		pygame.display.flip()

from mlgame.communication.transition import send_to_transition

class TransitionServer:
	"""Pass the scene info received to the message server
	"""
	def __init__(self):
		"""Constructor
		"""
		pass

	def _send_game_info(self):
		"""Send the information of the game to the message server
		"""
		info_dict = {
			"scene": {
				"size": [200, 500]
			},
			"game_object": [
				{ "name": "ball", "size": [5, 5], "color": [44, 185, 214] },
				{ "name": "platform", "size": [40, 5], "color": [66, 226, 126] },
				{ "name": "brick", "size": [25, 10], "color": [244, 158, 66] },
			]
		}

		send_to_transition({
			"type": "game_info",
			"data": info_dict,
		})

	def _send_scene_info(self, scene_info: SceneInfo, frame_delayed: int):
		"""Send the scene_info to the message server
		"""
		status_dict = {
			"frame": scene_info.frame,
			"frame_delayed": [frame_delayed],
		}
		gameobject_dict = {
			"ball": [scene_info.ball],
			"platform": [scene_info.platform],
			"brick": scene_info.bricks
		}

		send_to_transition({
			"type": "game_progress",
			"data": {
				"status": status_dict,
				"game_object": gameobject_dict,
			}
		})

	def _send_game_result(self, scene_info: SceneInfo, frame_delayed: int):
		"""Send the game result to the message server
		"""
		game_result_dict = {
			"frame_used": scene_info.frame,
			"frame_delayed": [frame_delayed],
			"result": [scene_info.status],
			"brick_remain": len(scene_info.bricks),
		}

		send_to_transition({
			"type": "game_result",
			"data": game_result_dict,
		})
