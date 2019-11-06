# Snake

![Imgur](https://i.imgur.com/aVDPwWP.gif)

## Execution

* Manual mode: `python MLGame.py snake -m`
    * Controlling: ¡ô, ¡õ, ¡ö, ¡÷
    * Perhaps 30 fps is too fast to play.
* ML mode: `python MLGame.py snake -i ml_play_template.py`

## Overview

### Game area

300 \* 300 pixels

### Game objects

#### Snake

* The snake is composed of squares. The size of a square is 10 \* 10 pixels.
* The head is a green square, the bodies are white squares.
* The head is initially at (40, 40), and the bodies are at (40, 30), (40, 20), (40, 10).
* The snake initially goes downward. It moves 10 pixels long per frame.

#### Food

* The food is a red circle, and its size is also 10 \* 10 pixels.
* The position of the food is randomly decided, which is (0 <= 10 \* m < 300, 0 <= 10 \* n < 300), where m and n are non-negative integers.

## Communicate with Game

View the example of the ml script in [`ml/ml_play_template.py`](ml/ml_play_template.py).

### Data Structures

#### `SceneInfo`

Store the information of the scene. Defined in [`game/gamecore.py`](game/gamecore.py).

The members of the `SceneInfo`:

* `frame`: The number of the frame that this `SceneInfo` is for
* `status`: The game status at this frame. It's one of `GameStatus`.
* `snake_head`: The position of the snake head. It's a `(x, y)` tuple.
* `snake_body`: A list storing the position of snake bodies, and the storing order is from the head to the tail. Each element in the list is a `(x, y)` tuple.
* `food`: The position of the food. It's a `(x, y)` tuple.
* `command`: The command decided for this frame. This member is used for recording the game progress.

#### `GameStatus`

The game status. Defined in [`game/gamecore.py`](game/gamecore.py).

There are two `GameStatus`: `GAME_ALIVE` and `GAME_OVER`.

#### `SnakeAction`

Control the moving direction of the snake. Defined in [`game/gameobject.py`](game/gameobject.py).

There are five `SnakeAction`: `UP`, `DOWN`, `LEFT`, `RIGHT`, and `NONE`. The action `NONE` will not change the moving direction.

### Methods

The following methods are defined in [`communication.py`](communication.py).

* `ml_ready()`: Inform the game process that ml process is ready.
* `get_scene_info()`: Receive the `SceneInfo` sent from the game process.
* `send_command(frame, command)`: Send the command to the game process.
    * `frame`: The number of frame that this command is for. This value should be the same as the `frame` of the received `SceneInfo`.
    * `command`: The command for controlling the snake. It's one of `SnakeAction`.
