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
            target_script = self._helper.target_module.split('.')[-1] + ".py"
            trimmed_callstack = trim_callstack(traceback.format_exc(), target_script)
            exception = MLProcessError(self._helper.name, trimmed_callstack)
            self._helper.send_exception(exception)

    def _loop(self):
        """
        The loop for receving scene information from the game, make ml module execute,
        and send the command back to the game.
        """
        ml_module = importlib.import_module(self._helper.target_module, __package__)
        ml = ml_module.MLPlay(*self._helper.args, **self._helper.kwargs)

        self._helper.send_to_game("READY")
        while True:
            command = ml.execute(self._helper.recv_from_game())

            if command == "RESET":
                ml.reset()
                self._helper.send_to_game("READY")
                continue

            if command:
                self._helper.send_to_game(command)
