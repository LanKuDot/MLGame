# PingPong

**Game version: 1.1**

## Overview

<img src="https://i.imgur.com/ke6nUrB.gif" height="500px" />

At the beginning of a round, you could move the platform to decide where to serve the ball and its direction. If the ball is not served in 150 frames, it will be randomly served from the platform. The ball speed starts from 7, and is increased every 100 frames. If the ball speed exceeds 40, this round is a draw game.

There are two mechanisms. One is ball slicing: The x speed of the ball will be changed according to the movement of the platform while the platform catches the ball. The other is a moving blocker at the middle of the game place.

## Execution

* Manual mode: `python MLGame.py -m pingpong <difficulty> [game_over_score]`
    * Serve the ball to the left/right: 1P - `.`, `/`; 2P - `Q`, `E`
    * Move the platform: 1P - `left`, `right` arrow keys; 2P - `A`, `D`
* ML mode: `python MLGame.py -i ml_play_template.py pingpong <difficulty> [game_over_score]`

### Game Parameters

* `difficulty`: The game style. There are 3 difficulties.
    * `EASY`: The simple pingpong game.
    * `NORMAL`: The ball slicing mechanism is added.
    * `HARD`: The ball slicing and the blocker mechanism are added.
* `game_over_score`: [Optional] When the score of either side reaches this value, the game will be exited. The default value is 3. If the `-1` flag is set, it will be 1.

## Detailed Game Information

### Game Coordinate

Same as the game "Arkanoid"

### Game Area

500 \* 200 pixels

1P side is at the lower half of the game area, and 2P side is at the upper half of the game area.

### Game Objects

#### Ball

* The ball is a 5-by-5-pixel green square.
* The ball will be served from the 1P side first, and then change side for each round.
* The ball is served from the platform, and it can be served to the left or right. If the ball is not served in 150 frames, it will be automatically served to the random direction.
* The initial moving speed is (&plusmn;7, &plusmn;7) pixels per frame, and it is increased every 100 frames after the ball is served.

#### Platform

* The platform is a 40-by-30-pixel rectangle.
* The color of the 1P platform is red, and it of the 2P platform is blue.
* The moving speed is (&plusmn;5, 0) pixels per frame.
* The initial position of the 1P platform is at (80, 420), and it of the 2P platform is at (80, 50).

#### Ball Slicing Mechanism

The x speed of the ball is changed according to the movement of the platform while it catches the ball.

* If the platform moves in the same direction of the ball, the x speed of the ball is increased by 3 (only once).
* If the platform is stable, the x speed of the ball is reset to current basic ball speed.
* If the platform moves in the opposite direction of the ball, the ball will be hit back to the direction where it comes from and the x speed is reset to the current basic ball speed.

The ball slicing mechanism is added on `NORMAL` and `HARD` difficulties.

#### Blocker

* The blocker is a 30-by-20-pixel rectangle.
* The initial position of x is randomly choiced from 0 to 180, 20 per step, and the initial position of y is 240. The moving speed is (&plusmn;5, 0) pixels per frame.
* The blocker will keep moving left and right. The initial direction is random.
* The blocker doesn't have ball slicing mechanism, which the ball speed is the same after it hits the blocker.

The blocker is added on `HARD` difficulty.

## Communicate with Game

The example script is in [`ml_play_template.py`](./ml/ml_play_template.py).

### Initial arguments

* `side`: A string which is either `"1P"` or `"2P"` to indicate that the script is used by which side.

### Communication Objects

#### Scene Information

A dictionary object sent from the game process.

```
{
    'frame': 42,
    'status': 'GAME_ALIVE',
    'ball': (189, 128),
    'ball_speed': (7, -7),
    'platform_1P': (0, 420),
    'platform_2P': (0, 50),
    'blocker': (50, 240)
}
```

The keys and values of the scene information:

* `"frame"`: An integer. The number of frame that this scene information is for
* `"status"`: A string. The game status at this frame. It's one of the following 4 statuses:
    * `"GAME_ALIVE"`: This round is still going.
    * `"GAME_1P_WIN"`: 1P wins this round.
    * `"GAME_2P_WIN"`: 2P wins this round.
    * `"GAME_DRAW"`: This round is a draw game.
* `"ball"`: An `(x, y)` tuple. The position of the ball.
* `"ball_speed"`: An `(x, y)` tuple. The speed of the ball.
* `"platform_1P"`: An `(x, y)` tuple. The position of the 1P platform.
* `"platform_2P"`: An `(x, y)` tuple. The position of the 2P platform.
* `"blocker"`: An `(x, y)` tuple. The position of the blocker. If the game is not on `HARD` difficulty, this field is `None`.

#### Game Command

A string command sent to the game process for controlling the platform.

```
'MOVE_RIGHT'
```

Here are available commands:

* `"SERVE_TO_LEFT"`: Serve the ball to the left.
* `"SERVE_TO_RIGHT"`: Serve the ball to the right.
* `"MOVE_LEFT"`: Move the platform to the left.
* `"MOVE_RIGHT"`: Move the platform to the right.
* `"NONE"`: Do nothing.

## Input Scripts for ML Mode

The pingpong game is a 2P game, so it can accept two different ml scripts by specifying `-i <script_for_1P> -i <script_for_2P>`. If there is only one script specified, 1P and 2P will use the same script.

You can specify `ml_play_manual.py` as the input script. It will create an invisible joystick for you to play with the ml process. For example:
1. Start the game by the command `python MLGame.py -i ml_play_template.py -i ml_play_manual.py pingpong <difficulty>`. There will be 2 windows, and one is the "Invisible joystick". The terminal will output a message "Invisible joystick is used. Press Enter to start the 2P ml process."

<img src="https://i.imgur.com/iyrS87t.png" height="500px" />

2. Drag the invisible joystick aside, and focus on it (The color of the window title is not gray).

<img src="https://i.imgur.com/6kOPjgB.png" height="500px" />

3. Press Enter key to start the game, and use left and right arrow keys to control the platform of the selected side.

## About the Ball

The behavior of the ball is the same as the game "Arkanoid".
