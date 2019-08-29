import pygame
import time
import os.path

from mlgame.gamedev.generic import quit_or_esc
from mlgame.gamedev.recorder import get_record_handler
from mlgame.communication import game as comm
from mlgame.communication.game import CommandReceiver

from . import gamecore
from .gamecore import GameStatus, PlatformAction
from ..communication import SceneInfo, GameInstruction
from ..main import get_log_dir

class PingPong:
	"""
	The game core for the machine learning mode
	"""
	def __init__(self, fps: int, game_over_score: int, record_progress, to_transition):
		"""
		Constructor

		@param fps The fps of the game
		@param game_over_score The game will stop when either side reaches this score
		@param record_progress Whether to record the game process or not
		@param to_transition Whether to pass the game progress to the transition process
		"""
		self._ml_name = ["ml_1P", "ml_2P"]
		self._ml_execute_time = 1.0 / fps
		self._frame_delayed = [0, 0]	# 1P, 2P
		self._score = [0, 0]	# 1P, 2P
		self._game_over_score = game_over_score
		self._cmd_receiver = CommandReceiver( \
			GameInstruction, { \
				"command": [PlatformAction.MOVE_LEFT, PlatformAction.MOVE_RIGHT, PlatformAction.NONE]
			}, GameInstruction(-1, PlatformAction.NONE))

		self._record_handler = get_record_handler(record_progress, {
				"status": (GameStatus.GAME_1P_WIN, GameStatus.GAME_2P_WIN)
			}, get_log_dir())
		self._to_transition = to_transition

		if not self._to_transition:
			self._init_display()
			self._scene = gamecore.Scene(True)
		else:
			self._scene = gamecore.Scene(False)
			self._transition_server = TransitionServer()

	def _init_display(self):
		"""
		Initialize the display of pygame
		"""
		pygame.display.init()
		pygame.display.set_caption("PingPong")
		self._screen = pygame.display.set_mode(gamecore.display_area_size)

		pygame.font.init()
		self._font = pygame.font.Font(None, 22)
		self._font_pos_1P = (1, gamecore.display_area_size[1] - 21)
		self._font_pos_2P = (1, 4)
		self._font_pos_speed = (gamecore.display_area_size[0] - 75, \
			gamecore.display_area_size[1] - 21)

	def game_loop(self):
		"""
		The main loop of the game execution
		"""
		if self._to_transition:
			keep_going = lambda : True
			self._transition_server._send_game_info()
		else:
			keep_going = lambda : not quit_or_esc()

		comm.wait_all_ml_ready()

		while keep_going():
			scene_info = self._scene.fill_scene_info_obj(SceneInfo())

			# Send the scene info to the ml processes and wait for instructions
			instruction_1P, instruction_2P = self._make_ml_execute(scene_info)

			scene_info.command_1P = instruction_1P.command.value
			scene_info.command_2P = instruction_2P.command.value
			self._record_handler(scene_info)

			# Update the scene
			game_status = self._scene.update( \
				instruction_1P.command, instruction_2P.command)

			if not self._to_transition:
				self._draw_scene()
			else:
				self._transition_server._send_scene_info(scene_info, self._frame_delayed)

			# If either of two sides wins, reset the scene and wait for ml processes
			# getting ready for the next round
			if game_status == GameStatus.GAME_1P_WIN or \
			   game_status == GameStatus.GAME_2P_WIN:
				scene_info = self._scene.fill_scene_info_obj(SceneInfo())
				self._record_handler(scene_info)
				comm.send_to_all_ml(scene_info)

				if self._to_transition:
					self._transition_server._send_scene_info(scene_info, self._frame_delayed)

				print("Frame: {}, Status: {}\n-----" \
					.format(scene_info.frame, game_status.value))

				if self._game_over(game_status):
					break

				self._scene.reset()
				self._frame_delayed = [0, 0]
				# Wait for ml processes doing their resetting jobs
				comm.wait_all_ml_ready()

		if self._to_transition:
			self._transition_server._send_game_result(scene_info, self._frame_delayed, \
				self._score)

		self._print_result()
		pygame.quit()

	def _make_ml_execute(self, scene_info):
		"""
		Send the scene_info to the ml process and wait for the instructions
		"""
		comm.send_to_all_ml(scene_info)
		time.sleep(self._ml_execute_time)
		instructions = self._cmd_receiver.recv_all()

		self._check_frame_delayed(0, scene_info.frame, instructions)
		self._check_frame_delayed(1, scene_info.frame, instructions)

		return instructions[self._ml_name[0]], instructions[self._ml_name[1]]

	def _check_frame_delayed(self, ml_index, scene_frame, instructs):
		"""
		Update the `frame_delayed` if the received instruction frame is delayed
		"""
		instruct_frame = instructs[self._ml_name[ml_index]].frame

		if instruct_frame != -1 and \
		   scene_frame - instruct_frame > self._frame_delayed[ml_index]:
			self._frame_delayed[ml_index] = scene_frame - instruct_frame
			print("{} delayed {} frame(s)" \
				.format(self._ml_name[ml_index], self._frame_delayed[ml_index]))

	def _draw_scene(self):
		"""
		Draw the scene and status to the display
		"""
		self._screen.fill((0, 0, 0))
		self._scene.draw_gameobjects(self._screen)

		font_surface_1P = self._font.render( \
			"1P score: {}".format(self._score[0]), True, gamecore.color_1P)
		font_surface_2P = self._font.render( \
			"2P score: {}".format(self._score[1]), True, gamecore.color_2P)
		font_surface_speed = self._font.render( \
			"Speed: {}".format(abs(self._scene._ball._speed[0])), True, (255, 255, 255))
		self._screen.blit(font_surface_1P, self._font_pos_1P)
		self._screen.blit(font_surface_2P, self._font_pos_2P)
		self._screen.blit(font_surface_speed, self._font_pos_speed)

		pygame.display.flip()

	def _game_over(self, status):
		if status == GameStatus.GAME_1P_WIN:
			self._score[0] += 1
		else:
			self._score[1] += 1

		return self._score[0] == self._game_over_score or \
			self._score[1] == self._game_over_score

	def _print_result(self):
		if self._score[0] > self._score[1]:
			win_side = "1P"
		else:
			win_side = "2P"

		print("{} wins! Final score: {}-{}".format(win_side, *self._score))

from mlgame.communication.transition import send_to_transition

class TransitionServer:
	"""
	Pass the scene info received to the message server
	"""
	def __init__(self):
		"""
		Constructor
		"""
		pass

	def _send_game_info(self):
		"""
		Send the game information to the message server
		"""
		info_dict = {
			"scene": {
				"size": [200, 500],
			},
			"game_object": [
				{ "name": "platform_1P", "size": [40, 30], "color": [84, 149, 255] },
				{ "name": "platform_2P", "size": [40, 30], "color": [219, 70, 92] },
				{ "name": "ball", "size": [5, 5], "color": [66, 226, 126] },
			]
		}

		send_to_transition({
			"type": "game_info",
			"data": info_dict,
		})

	def _send_scene_info(self, scene_info: SceneInfo, frame_delayed):
		"""
		Send the scene info to the message server
		"""
		status_dict = {
			"frame": scene_info.frame,
			"frame_delayed": frame_delayed,
			"ball_speed": scene_info.ball_speed,
		}
		gameobject_dict = {
			"ball": [scene_info.ball],
			"platform_1P": [scene_info.platform_1P],
			"platform_2P": [scene_info.platform_2P],
		}

		send_to_transition({
			"type": "game_progress",
			"data": {
				"status": status_dict,
				"game_object": gameobject_dict,
			}
		})

	def _send_game_result(self, scene_info: SceneInfo, frame_delayed, final_score):
		"""
		Send the game result to the message server
		"""
		if final_score[0] > final_score[1]:
			status = ["GAME_PASS", "GAME_OVER"]
		else:
			status = ["GAME_OVER", "GAME_PASS"]

		game_result_dict = {
			"frame_used": scene_info.frame,
			"frame_delayed": frame_delayed,
			"result": status,
			"ball_speed": scene_info.ball_speed,
		}

		send_to_transition({
			"type": "game_result",
			"data": game_result_dict,
		})
