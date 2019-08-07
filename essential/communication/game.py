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
# The handler takes 1 argument: `from_ml` - the name of the ml process, and
# 1 optional argument: `to_wait` - [default: False]
# whether to wait the object sent from the ml process.
# If `to_wait` is False and there is no object available, return None.
# Usage: recv_from_ml(from_ml[, to_wait = False])
recv_from_ml = FunctionDelegate()

# The handler for receiving objects from all ml processes
# The handler take 1 optional argument: `to_wait`. See `recv_from_ml` for the usage.
# Usage: recv_from_all_ml([to_wait = False])
# Return: a list of received objects, the order is the same as the registered order
# in the ProcessManager.
recv_from_all_ml = FunctionDelegate()
