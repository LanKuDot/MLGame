# PingPong

<img src="https://i.imgur.com/52oAU3G.gif" height="500px" />

## Execution

* Manual mode: `python MLGame.py pingpong [game_over_score] -m`
    * Controlling: 1P - ก๖, ก๗; 2P - A, D
* ML mode: `python MLGame.py pingpong [game_over_score] -i ml_play_template.py`

When the score of either side reaches `[game_over_score]`, the game will be exited. If `[game_over_score]` is not specified, it will be 3. If the `-1` flag is set, `[game_over_score]` will be 1.

### Input Scripts

PingPong Game is a 2P game, so it can accept two different ml scripts by specifying `-i <script_for_1P> <script_for_2P>`. If there is only one script specified, 1P and 2P will use the same script.

You can specify `ml_play_manual.py` as the input script. It will create an invisible joystick for you to play with the ml process. For example: 
1. Start the game by the command `python MLGame.py pingpong -i ml_play_template.py ml_play_manual.py`. There will be 2 windows, and one is the "Invisible joystick". The terminal will output a message "Invisible joystick is used. Press Enter to start the 2P ml process."

<img src="https://i.imgur.com/iyrS87t.png" height="500px" />

2. Drag the invisible joystick aside, and focus on it (The color of the window title is not gray).

<img src="https://i.imgur.com/6kOPjgB.png" height="500px" />

3. Press Enter key to start the game, and use ก๖ and ก๗ keys to control the platform of selected side.

## Overview

### Game Area

500 \* 200 pixels

1P side is at the lower half of the game area, and 2P side is at the upper half of the game area.

### Game Objects

#### Ball

* The ball is a 5-by-5-pixel green square.
* The initial moving speed is (กำ7, กำ7) pixels per frame, and it increases every 200 frames.
* The ball will be served from the 1P side first, and then changing side for each round.
* When the ball is served from the 1P side, its initial position is at (120, 395), and it moves toward the upper left. When the ball is served from the 2P side, its initial position is at (75, 100), and it moves toward the lower right.

#### Platform

* The platform is a 40-by-30-pixel rectangle.
* The color of the 1P platform is red, and it of the 2P platform is blue.
* The moving speed is (กำ5, 0) pixels per frame.
* The initial position of the 1P platform is at (80, 420), and it of the 2P platform is at (80, 50).

### Game Status

* `GAME_1P_WIN`: The ball is above the 2P platform. 1P wins this round.
* `GAME_2P_WIN`: The ball is below the 1P platform. 2P wins this round.

## Communicate with Game

View the example of the ml script in [`ml/ml_play_template.py`](ml/ml_play_template.py).

### `ml_loop()`

The `ml_loop()` function must has a `side` parameter. The game will pass `"1P"` or `"2P"` to it to distinguish that the script is used by which side. You can write codes for both sides in the same script. For example:

```python
def ml_loop(side):
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
```

### Data Structures

#### `SceneInfo`

Store the information of the scene. Defined in [`game/gamecore.py`](game/gamecore.py).

The members of the `SceneInfo`:

* `frame`: The number of frame that this `SceneInfo` is for
* `status`: The game status at this frame. It's one of `GameStatus`.
* `ball`: The position of the ball. It's a `(x, y)` tuple.
* `ball_speed`: The speed of the ball. It's an absolute value.
* `platform_1P`: The position of the 1P platform. It's a `(x, y)` tuple.
* `platform_2P`: The position of the 2P platform. It's a `(x, y)` tuple.
* `command_1P`: The command 1P decided according to this frame.
* `command_2P`: The command 2P decided according to this frame.

#### `GameStatus`

The game status. Defined in [`game/gamecore.py`](game/gamecore.py).

There are 3 `GameStatus`: `GAME_ALIVE`, `GAME_1P_WIN`, and `GAME_2P_WIN`. `GAME_ALIVE` means that the game is still going.

#### `PlatformAction`

Control the platform. Defined in [`game/gameobject.py`](game/gameobject.py).

There are 3 `PlatformAction`: `MOVE_LEFT`, `MOVE_RIGHT`, and `NONE`.

### Methods

The following methods are defined in [`communication.py`](communication.py).

* `ml_ready()`: Inform the game process that ml process is ready.
* `get_scene_info()`: Receive the `SceneInfo` sent from the game process.
* `send_instruction(frame, command)`: Send the command to the game process.
    * `frame`: The number of frame that this command is for. This value should be the same as the `frame` of the received `SceneInfo`.
    * `command`: The command for controlling the platform. It's one of `PlatformAction`.

## About the Ball

The behavior of the ball is the same as the game "Arkanoid". 
