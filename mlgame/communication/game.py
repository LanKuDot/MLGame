from . import base

def send_to_ml(obj, ml_name: str):
	"""
	Send an object to the specified ml process

	@param obj The object to be sent
	@param ml_name The name of the target ml process
	"""
	base.send_to_ml(obj, ml_name)

def send_to_all_ml(obj):
	"""
	Send an object to all ml processes

	@param obj The object to be sent
	"""
	base.send_to_all_ml(obj)

def recv_from_ml(ml_name, to_wait = False):
	"""
	Receive an object sent from the specified ml process

	@param ml_name The name of the target ml process
	@param to_wait Whether to wait the object or not
	@return The received object.
	        If `to_wait` is False and there is nothing to receive, return None.
	"""
	return base.recv_from_ml(ml_name, to_wait)

def recv_from_all_ml(to_wait = False):
	"""
	Receive objects from all ml processes

	@param to_wait Whether to wait objects or not
	@return A dictionary. The key is the game of the ml process,
	        the value is the received object from that process.
	        If `to_wait` is False and there is nothing to receive from that process,
	        the value will be None.
	"""
	return base.recv_from_all_ml(to_wait)


def wait_ml_ready(ml_name):
	"""
	Wait until receiving the ready command from a ml process
	"""
	while recv_from_ml(ml_name, to_wait = True) != "READY":
		pass

def wait_all_ml_ready():
	"""
	Wait until receiving the ready command from all ml processes
	"""
	ready_dict = recv_from_all_ml(to_wait = False)

	# Wait the ready command one by one
	for ml_process, received_msg in ready_dict.items():
		while received_msg != "READY":
			received_msg = recv_from_ml(ml_process, to_wait = True)


class CommandReceiver:
	"""
	Receive and check the command sent from the ml process

	If the received command is invalid, return the specified default command.
	The command is invalid, if one of the conditions below is matched:
	- No command available from the ml process,
	- Received command is not the instance of the `cmd_class`,
	- The value of the member of received command is not in the `valid_members`.
	"""

	def __init__(self, cmd_class, valid_members, default_cmd):
		"""
		Constructor

		@param instruct_class The desired class of the received command
		@param valid_members A dictionary indicating the desired values of the members
		       of the received command. The key is the name of the member,
		       the value is a list of desired values of that member.
		@param default_cmd The command to be returned when received command
		       is invalid.
		"""
		self._cmd_class = cmd_class
		self._valid_members = valid_members
		self._default_cmd = default_cmd

	def _is_cmd_valid(self, cmd):
		"""
		Check if the command is valid
		"""
		if not isinstance(cmd, self._cmd_class):
			return False

		try:
			for name, value in self._valid_members.items():
				if cmd.__dict__[name] not in value:
					return False
		except (KeyError, AttributeError):
			return False

		return True

	def recv(self, from_ml: str):
		"""
		Receive the command from the specified ml process

		@param from_ml The name of the ml process
		@return Received command
		        If the command is invalid, return `default_cmd`.
		"""
		received_obj = recv_from_ml(from_ml)

		if self._is_cmd_valid(received_obj):
			return received_obj

		return self._default_cmd

	def recv_all(self):
		"""
		Receive the commands from all ml processes

		@return A dictionary of which the key is the name of the process,
		        and the value is the received command or the `default_cmd`.
		"""
		received_list = recv_from_all_ml()

		for from_ml, obj in received_list.items():
			if not self._is_cmd_valid(obj):
				received_list[from_ml] = self._default_cmd

		return received_list
