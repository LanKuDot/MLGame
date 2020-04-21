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
    @param to_wait Whether to wait until the object is received or not
    @return The received object.
            If `to_wait` is False and there is nothing to receive, return None.
    """
    return base.recv_from_ml(ml_name, to_wait)

def recv_from_all_ml(to_wait = False):
    """
    Receive objects sent from all ml processes

    @param to_wait Whether to wait until all the objects are received or not
    @return A dictionary. The key is the game of the ml process,
            the value is the received object from that process.
            If `to_wait` is False and there is nothing to receive from that process,
            the value will be None.
    """
    return base.recv_from_all_ml(to_wait)


def wait_ml_ready(ml_name):
    """
    Wait until receiving the ready command from specified the ml process

    @param ml_name The name of the target ml process
    """
    while recv_from_ml(ml_name, to_wait = True) != "READY":
        pass

def wait_all_ml_ready():
    """
    Wait until receiving the ready commands from all ml processes
    """
    ready_dict = recv_from_all_ml(to_wait = False)

    # Wait the ready command one by one
    for ml_process, received_msg in ready_dict.items():
        while received_msg != "READY":
            received_msg = recv_from_ml(ml_process, to_wait = True)
