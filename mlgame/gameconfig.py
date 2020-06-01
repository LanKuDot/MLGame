"""
Handle the game defined config
"""

import importlib
import inspect

from .exceptions import GameConfigError

class GameConfig:
    """
    The data class storing the game defined config
    """

    def __init__(self, game_name):
        """
        Parse the game defined config and generate a `GameConfig` instance
        """
        game_config = self._load_game_config(game_name)

        self.game_version = getattr(game_config, "GAME_VERSION", "")
        self.game_params = getattr(game_config, "GAME_PARAMS", {
            "()": {
                "prog": game_name,
                "game_usage": "%(prog)s"
            }
        })
        self._process_game_param_dict()

        try:
            self.game_setup = getattr(game_config, "GAME_SETUP")
        except AttributeError as e:
            raise GameConfigError("Missing '{}' in the game config".format(e))

        self._process_game_setup_dict()

    def _load_game_config(self, game_name):
        """
        Load the game config
        """
        try:
            game_config = importlib.import_module("games.{}.config".format(game_name))
        except ModuleNotFoundError as e:
            failed_module_name = e.__str__().split("'")[1]
            if failed_module_name == "games." + game_name:
                msg = ("Game '{}' dosen't exist or it doesn't provide '__init__.py'"
                    .format(game_name))
            else:
                msg = ("Game '{}' dosen't provide 'config.py'"
                    .format(game_name))
            raise GameConfigError(msg)
        else:
            return game_config

    def _process_game_param_dict(self):
        """
        Convert some fields in `GAME_PARAMS`
        """
        param_dict = self.game_params

        # Append the prefix of MLGame.py usage to the `game_usage`
        # and set it to the `usage`
        if param_dict.get("()") and param_dict["()"].get("game_usage"):
            game_usage = str(param_dict["()"].pop("game_usage"))
            param_dict["()"]["usage"] = "python MLGame.py [options] " + game_usage

        # If the game not specify "--version" flag,
        # try to convert `GAME_VERSION` to a flag
        if not param_dict.get("--version"):
            param_dict["--version"] = {
                "action": "version",
                "version": self.game_version
            }

    def _process_game_setup_dict(self):
        """
        Process the value of `GAME_SETUP`

        The `GAME_SETUP` is a dictionary which has several keys:
        - "game": Specify the class of the game to be execute
        - "dynamic_ml_clients": (Optional) Whether the number of ml clients is decided by
          the number of input scripts.
        - "ml_clients": A list containing the information of the ml client.
            Each element in the list is a dictionary in which members are:
            - "name": A string which is the name of the ml client.
            - "args": (Optional) A tuple which contains the initial positional arguments
                to be passed to the ml client.
            - "kwargs": (Optional) A dictionary which contains the initial keyword arguments
                to be passed to the ml client.
        """
        try:
            game_cls = self.game_setup["game"]
            ml_clients = self.game_setup["ml_clients"]
        except KeyError as e:
            raise GameConfigError("Missing '{}' in the 'GAME_SETUP' of the game config"
                .format(e))

        if not self.game_setup.get("dynamic_ml_clients"):
            self.game_setup["dynamic_ml_clients"] = False

        if self.game_setup["dynamic_ml_clients"] and len(ml_clients) == 1:
            print("Warning: 'dynamic_ml_clients' in the 'GAME_SETUP' of the game config "
                "is invalid for just one ml client. Set to False.")
            self.game_setup["dynamic_ml_clients"] = False
