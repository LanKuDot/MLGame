class CommunicationSet:
    """
    A data class for storing communicating sets
    """
    def __init__(self):
        self.recv_end = {}
        self.send_end = {}

class CommunicationHandler:
    """
    A data class for storing a sending and a receiving handler
    """
    def __init__(self):
        self.recv_end = None
        self.send_end = None

    def poll(self):
        return self.recv_end.poll()

    def recv(self):
        return self.recv_end.recv()

    def send(self, obj):
        self.send_end.send(obj)

from ..utils.delegate import FunctionDelegate

## The handlers for communicating between processes
## They will be initialized at the start of the corresponding processes.

##### The handlers for game process communicating with ml process #####

# The handler for sending an object to a ml process
# See GameProcessHelper.send_to_ml
send_to_ml = FunctionDelegate()

# The handler for sending an object to all ml processes
# See GameProcessHelper.send_to_all_ml
send_to_all_ml = FunctionDelegate()

# The handler for receiving an object from a ml process
# See GameProcessHelper.recv_from_ml
recv_from_ml = FunctionDelegate()

# The handler for receiving objects from all ml processes
# See GameProcessHelper.recv_from_all_ml
recv_from_all_ml = FunctionDelegate()

##### The handlers for ml process communicating with game process #####

# The handler for sending object to the game process
# See MLProcessHelper.send_to_game
send_to_game = FunctionDelegate()

# The handler for receiving object from the game process
# See MLProcessHelper.recv_from_game
recv_from_game = FunctionDelegate()