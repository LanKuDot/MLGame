"""
The template of the script for playing the game in the ml mode
"""

# Import the required class and module
from mlgame.communication import ml as comm

def ml_loop():
    """
    The main loop for the ml process
    """

    # === The execution order of the loop === #
    # 1. Put the initialization code here

    # 2. Inform the game process that the ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1 Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2 If the game is over
        if scene_info["status"] == "GAME_OVER":
            # 3.2.1 Do some reset works if needed.

            # 3.2.2 Inform the game process that ml process
            #       is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Process the information received here

        # 3.4 Generate a command for this game information and
        #     send to the game process.
        comm.send_to_game({"frame": scene_info["frame"], "command": "RIGHT"})
