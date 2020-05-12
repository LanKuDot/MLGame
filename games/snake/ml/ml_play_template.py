"""
The template of the script for playing the game in the ml mode
"""

class MLPlay:
    def __init__(self):
        """
        Constructor
        """
        pass

    def execute(self, scene_info):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] == "GAME_OVER":
            return "RESET"

        return {"frame": scene_info["frame"], "command": "RIGHT"}

    def reset(self):
        """
        Reset the status if needed
        """
        pass
