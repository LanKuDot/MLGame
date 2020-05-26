"""
The ml client runs in ml process as the bridge of cross language client and game process.
"""
from .client import Client

from .exceptions import MLClientExecutionError

class MLPlay:
    def __init__(self, script_execution_cmd, init_args, init_kwargs):
        self._client = Client(script_execution_cmd)

        # Pass initial arguments
        self._client.send_to_client("__init__", {
            "args": init_args,
            "kwargs": init_kwargs
        })

        self._wait_ready()

    def update(self, scene_info):
        self._client.send_to_client("__scene_info__", scene_info)
        return self._recv_from_client()

    def reset(self):
        self._wait_ready()

    def _wait_ready(self):
        """
        Wait for the ready command from the client
        """
        command = self._recv_from_client()
        while command != "READY":
            command = self._client.recv_from_client()

    def _recv_from_client(self):
        """
        Receive the command sent from the client
        """
        command = self._client.recv_from_client()

        if isinstance(command, MLClientExecutionError):
            raise command

        return command
