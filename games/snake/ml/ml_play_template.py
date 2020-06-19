"""
The template of the script for playing the game in the ml mode
"""

class MLPlay:
    def __init__(self):
        """
        Constructor
        """
        pass

    def update(self, scene_info):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] == "GAME_OVER":
            return "RESET"

        snake_head = scene_info["snake_head"]
        food = scene_info["food"]

        if snake_head[0] > food[0]:
            return "LEFT"
        elif snake_head[0] < food[0]:
            return "RIGHT"
        elif snake_head[1] > food[1]:
            return "UP"
        elif snake_head[1] < food[1]:
            return "DOWN"

    def reset(self):
        """
        Reset the status if needed
        """
        pass
