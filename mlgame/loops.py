"""
The loop executor for running games and ml client
"""

import importlib
import traceback

from .exceptions import (
    MLProcessError, trim_callstack
)
from .process import MLProcessHelper

class MLExecutor:
    """
    The loop executor for the machine learning process
    """

    def __init__(self, helper: MLProcessHelper):
        self._helper = helper

    def start(self):
        """
        Start the loop for the machine learning process
        """
        self._helper.start_recv_obj_thread()

        try:
            self._loop()
        except Exception as e:
            exception = MLProcessError(self._helper.name, traceback.format_exc())
            self._helper.send_exception(exception)

    def _loop(self):
        """
        The loop for receiving scene information from the game, make ml class execute,
        and send the command back to the game.
        """
        ml_module = importlib.import_module(self._helper.target_module, __package__)
        ml = ml_module.MLPlay(*self._helper.args, **self._helper.kwargs)

        self._ml_ready()
        while True:
            command = ml.update(self._helper.recv_from_game())

            if command == "RESET":
                ml.reset()
                self._ml_ready()
                continue

            if command:
                # Check if the command format is valid
                if not isinstance(command["frame"], int):
                    raise TypeError("The value of 'frame' in the returned game command "
                        "should be an 'int'")
                if not isinstance(command["command"], list):
                    raise TypeError("The value of 'command' in the returned game command "
                        "should be a 'list'")

                self._helper.send_to_game(command)

    def _ml_ready(self):
        """
        Send a "READY" command to the game process
        """
        self._helper.send_to_game("READY")
