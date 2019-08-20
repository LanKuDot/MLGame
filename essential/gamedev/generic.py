import pygame

from ..communication.game import recv_from_ml, recv_from_all_ml

def quit_or_esc() -> bool:
	"""
	Check if the quit event is triggered or the ESC key is pressed.
	"""
	for event in pygame.event.get():
		if event.type == pygame.QUIT or \
		  (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			return True
	return False

class BasicSceneInfo:
	STATUS_GAME_ALIVE = "GAME_ALIVE"
	STATUS_GAME_PASS = "GAME_PASS"
	STATUS_GAME_OVER = "GAME_OVER"

	def __init__(self):
		self.frame = -1
		self.status = BasicSceneInfo.STATUS_GAME_ALIVE

	def __str__(self):
		return "# Frame {}\n# Status {}".format(self.frame, self.status)

class KeyCommandMap:
	"""
	Map the keys to the commands and return the mapped command when the key is pressed
	"""
	def __init__(self, command_map: dict, default_command = None):
		"""
		Constructor

		@param command_map A dict which maps the keys to the commands.
		       The key of the dict is the key-code defined in pygame, and
		       the value is the command that will be returned when the corresponding
		       key is pressed.
		@param default_command The command will be returned when there is no
		       registered key pressed.
		"""
		if not isinstance(command_map, dict):
			raise TypeError("The 'action_dict' should be a 'dict'.")

		self._command_map = command_map
		self._default_command = default_command

	def get_command(self):
		"""
		Check the pressed key and return the corresponding command

		If there is no registered key pressed, return the `default_command` instead.
		Note that only one command is returned at once, and the key checking order is
		the same as the ordering in `command_map` (Python 3.6+).
		"""
		key_pressed_list = pygame.key.get_pressed()
		for key, command in self._command_map.items():
			if key_pressed_list[key]:
				return command
		return self._default_command

class GameInstructionReceiver:
	"""
	Receive and check the game instruction sent from the ml process

	If the received instruction is invalid, return the specified default instruction.
	The instruction is invalid, if one of the conditions below is matched:
	- No instruction available from the ml process,
	- Received instruction is not the instance of the `instruct_class`,
	- The value of the member of received instruction is not in the `valid_members`.
	"""

	def __init__(self, instruct_class, valid_members, default_instruct):
		"""
		Constructor

		@param instruct_class The desired class of the received instruction
		@param valid_members A dictionary indicating the desired values of the members
		       of the received instruction. The key is the name of the member,
		       the value is a list of desired values of that member.
		@param default_instruct The instruction to be returned when received instruction
		       is invalid.
		"""
		self._instruct_class = instruct_class
		self._valid_members = valid_members
		self._default_instruct = default_instruct

	def _is_instruct_valid(self, instruct):
		"""
		Check if the instruction is valid
		"""
		if not isinstance(instruct, self._instruct_class):
			return False

		try:
			for name, value in self._valid_members.items():
				if instruct.__dict__[name] not in value:
					return False
		except (KeyError, AttributeError):
			return False

		return True

	def recv(self, from_ml: str):
		"""
		Receive the instruction from the specified ml process

		@param from_ml The name of the ml process
		@return Received instruction
		        If the instruction is invalid, return `default_instruct`.
		"""
		received_obj = recv_from_ml(from_ml)

		if self._is_instruct_valid(received_obj):
			return received_obj

		return self._default_instruct

	def recv_all(self):
		"""
		Receive the instructions from all ml processes

		@return A dictionary of which the key is the name of the process,
		        and the value is the received instruction or the `default_instruct`.
		"""
		received_list = recv_from_all_ml()

		for from_ml, obj in received_list.items():
			if not self._is_instruct_valid(obj):
				received_list[from_ml] = self._default_instruct

		return received_list
