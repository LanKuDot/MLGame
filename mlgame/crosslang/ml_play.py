"""
The ml client runs in ml process as the bridge of cross language client and game process.
"""
from .client import Client

from ..communication import ml as comm
from .exceptions import MLClientExecutionError

def ml_loop(execution_cmd, init_args, init_kwargs):
    """
    The main loop for communicating with non-py client and game process
    """
    with Client(execution_cmd) as client:
        # Pass initial arguments
        client.send_to_client("__init__", {
            "args": init_args,
            "kwargs": init_kwargs
        })

        # Start communication loop
        while True:
            command = client.recv_from_client()
            # Ready command
            if command == "READY":
                comm.ml_ready()
            # Error occurred while running client script
            elif isinstance(command, MLClientExecutionError):
                raise command
            # Game command
            else:
                comm.send_to_game(command)

            client.send_to_client("__scene_info__", comm.recv_from_game())
