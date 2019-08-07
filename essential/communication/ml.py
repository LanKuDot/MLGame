"""The handlers for exchanging objects with the game process

The corresponding handler will be initialized by the process manager
"""
from ..utils.delegate import FunctionDelegate

# The handler for sending object to the game process
# The handler only takes 1 argument which is an object to be sent.
send_to_game = FunctionDelegate()

# The handler for receiving object from the game process
# The handler takes no argument.
recv_from_game = FunctionDelegate()


def ml_ready():
	"""
	Inform the game process that the ml process is ready.
	"""
	send_to_game("READY")