# Snake

## Overview

![Imgur](https://i.imgur.com/aVDPwWP.gif)

Control the snake, eat as much food as possible.

## Execution

* Manual mode: `python MLGame.py -m snake`
    * Controlling: arrow keys
    * Perhaps 30 fps is too fast to play.
* ML mode: `python MLGame.py -i ml_play_template.py snake`

## Detailed Game Information

### Game Coordinate

The same as the game "Arkanoid"

### Game area

300 \* 300 pixels

### Game objects

#### Snake

* The snake is composed of squares. The size of a square is 10 \* 10 pixels.
* The head is a green square, the bodies are white squares.
* The head is initially at (40, 40), and the bodies are at (40, 30), (40, 20), (40, 10).
* The snake initially goes downward. It moves 10 pixels long per frame.
* The snake body will increase one when it eats the food.

#### Food

* The food is 10-by-10-pixel square, but its appearance is a red circle.
* The position of the food is randomly decided, which is (0 <= 10 \* m < 300, 0 <= 10 \* n < 300), where m and n are non-negative integers.

## Communicate with Game

View the example of the ml script in [`ml/ml_play_template.py`](ml/ml_play_template.py).

### Methods

Use `mlgame.communication.ml` module to communicate with the game process

* `ml_ready()`: Inform the game process that ml process is ready
* `recv_from_game`: Receive an dictionary object storing the scene information from the game process
* `send_to_game(dict)`: Send an dictionary object storing the game command to the game process

### Communication Objects

The dictionary object is used as the communication object transporting between game and ml processes.

#### Scene Information

It's an dictionary object sent from the game process, and also an object to be pickled in the record file.

The keys and values of the scene information:

* `"frame"`: An integer. The number of the frame that this scene information is for.
* `"status"`: A string. The game status at this frame. It's one of the following value:
    * `"GAME_ALIVE"`: The snake is still going.
    * `"GAME_OVER"`: The snake hits the wall or itself.
* `"snake_head"`: An `(x, y)` tuple. The position of the snake head.
* `"snake_body"`: A list storing the position of snake bodies, and the storing order is from the head to the tail. Each element in the list is an `(x, y)` tuple.
* `"food"`: An `(x, y)` tuple. The position of the food.
* `"command"`: A string. The command decided for this frame. This member is used for recording the game progress.

#### Game Command

It's an dictionary object sent to the game process for controlling the moving direction of the snake.

The keys and values of the game command:

* `"frame"`: An integer. The number of frame the command is for. It should be the same as the frame of the scene information received.
* `"command"`: A string. The command for controlling the snake. It's one of the following value:
    * `"UP"`: Make the snake move upward.
    * `"DOWN"`: Make the snake move downward.
    * `"LEFT"`: Make the snake move to left.
    * `"RIGHT"`: Make the snake move to right.
    * `"NONE"`: Do not change the moving direction of snake.
