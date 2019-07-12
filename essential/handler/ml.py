"""The handlers for exchanging objects with the game process

The corresponding handler will be initialized by the process manager
"""
from ..utils.delegate import FunctionDelegate

# The handler for sending object to the game process
# The handler only takes 1 argument which is an object to be sent.
send_to_game_handler = FunctionDelegate()

# The handler for receiving object from the game process
# The handler takes no argument.
recv_from_game_handler = FunctionDelegate()
