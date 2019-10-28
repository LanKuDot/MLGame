from games.snake.communication import ( \
    SnakeAction, SceneInfo, GameStatus, GameCommand
)
from games.snake import communication as comm

def ml_loop():
    comm.ml_ready()

    while True:
        scene_info = comm.get_scene_info()

        if scene_info.status == GameStatus.GAME_OVER:
            comm.ml_ready()
            continue

        comm.send_command(scene_info.frame, SnakeAction.RIGHT)
