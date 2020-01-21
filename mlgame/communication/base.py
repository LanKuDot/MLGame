class CommunicationSet:
    """
    A data class for storing a set of communication objects and
    providing an interface for accessing these objects

    Communication objects used for receiving objects must provide `recv()` and `poll()`,
    and them used for sending objects must provide `send()`.
    For example, the object of `multiprocessing.connection.Connection` is a valid
    communication object for both sending and receiving.

    @var _recv_end A dictionary storing communication objects which are used to
         receive objects
    @var _send_end A dictionary storing communication objects which are used to
         send objects
    """
    def __init__(self):
        self._recv_end = {}
        self._send_end = {}

    def add_recv_end(self, name: str, comm_obj):
        """
        Add a new communication object for receiving objects

        @param name The name for distinguishing the added object. It could be used to
               distinguish the communication target.
        @param comm_obj The communication object which has `recv()` and `poll()` functions
        """
        if self._recv_end.get(name):
            raise ValueError("The name '{}' already exists in 'recv_end'".format(name))

        if not hasattr(comm_obj, "recv") or not hasattr(comm_obj, "poll"):
            raise ValueError("'comm_obj' doesn't have 'recv' or 'poll' function")

        self._recv_end[name] = comm_obj

    def add_send_end(self, name: str, comm_obj):
        """
        Add a new communication object for sending objects

        @param name The name for distinguishing the added object. It could be used to
               distinguish the communication target.
        @param comm_obj The communication object which has `send()` function
        """
        if self._send_end.get(name):
            raise ValueError("The name '{}' already exists in 'send_end'".format(name))

        if not hasattr(comm_obj, "send"):
            raise ValueError("'comm_obj' doesn't have 'send' function")

        self._send_end[name] = comm_obj

    def get_recv_end_names(self):
        """
        Get the name of all registered communication objects used for receiving

        @return A dictionary view objects containing the key of `_recv_end`
        """
        return self._recv_end.keys()

    def get_send_end_names(self):
        """
        Get the name of all registered communication objects used for sending

        @return A dictionary view objects containing the key of `_send_end`
        """
        return self._send_end.keys()

    def poll(self, name: str):
        """
        Check whether the specified communication object has data to read

        @param name The name of the communication object
        """
        return self._recv_end[name].poll()

    def recv(self, name: str, to_wait: bool = False):
        """
        Receive object from the specified communication object

        @param name The name of the communication object
        @param to_wait Whether to wait until the object is arrived
        @return The received object. If `to_wait` is False and nothing available from
                the specified communication object, return None.
        """
        if not to_wait and not self.poll(name):
            return None

        return self._recv_end[name].recv()

    def recv_all(self, to_wait: bool = False):
        """
        Receive objects from all communication object registered for receiving

        If `to_wait` is True, it will wait for the object one by one.

        @param to_wait Whether to wait until the object is arrived
        @return A dictionary storing received objects. The key is the name of
                the communication object, the value is the received object.
                If `to_wait` is False and nothing to receive, the value will be None.
        """
        objs = {}
        for comm_name in self._recv_end.keys():
            obj[comm_name] = self.recv(comm_name, to_wait)

        return objs

    def send(self, obj, name: str):
        """
        Send object via the specified communication object

        @param obj The object to be sent
        @param name The name of the communication object
        """
        self._send_end[name].send(obj)

    def send_all(self, obj):
        """
        Send object via all communication objects registered for sending

        @param obj The object to be sent
        """
        for comm_obj in self._send_end.values():
            comm_obj.send(obj)

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