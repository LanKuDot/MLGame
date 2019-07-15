from ..utils.delegate import FunctionDelegate

# The handler for sending an object to a ml process
# The handler takes 2 arguments: the object and the name of the ml process
# Usage: send_to_ml(obj, to_ml)
send_to_ml = FunctionDelegate()

# The handler for sending an object to all ml processes
# The handler takes 1 argument: the object to be sent
# Usage: send_to_all_ml(obj)
send_to_all_ml = FunctionDelegate()

# The handler for receiving an object from a ml process
# The handler takes 1 argument: the name of the ml process
# Usage: recv_from_ml(from_ml)
recv_from_ml = FunctionDelegate()

# The handler for receiving objects from all ml processes
# The handler take no arguments.
# Usage: recv_from_all_ml()
# Return: a list of received objects, the order is the same as the registered order
# in the ProcessManager.
recv_from_all_ml = FunctionDelegate()
