# Arkanoid

## Overview

<img src="https://i.imgur.com/brqaW85.gif" height="500"/>

At the beginning of a round, you could decide where to serve the ball by moving the platform, and the serving direction can be also decided. Try to catch the ball and break all the bricks.

There are two difficulties. The `EASY` one is a simple arkanoid game, and the ball slicing mechanism is added in the `NORMAL` one, which the ball speed will be changed according to the movement of the platform. In some game level, there are "red" bricks that can be broken by hitting them twice. However, on the `NORMAL` difficulty, these red bricks can be broken by hitting them only once by speeding up the ball with the mechanism of ball slicing.

## Execution

* Manual mode: `python MLGame.py arkanoid <difficulty> <level_id> -m`
    * Serve the ball to the left/right: `A`, `D`
    * Move the platform: `left`, `right` arrow key
* ML mode: `python MLGame.py arkanoid <difficulty> <level_id> -i ml_play_template.py`

### Game Parameters

* `difficulty`: The game style.
    * `EASY`: The simple arkanoid game.
    * `NORMAL`: The ball slicing mechanism is added.
* `level_id`: Specify the level map. The available values can be checked in `game/level_data/` directory.

## Detailed Game Information

### Game Coordinate

Use the coordinate system of pygame. The origin is at the top left corner of the game area, the positive direction of the x-axis is towards the right, and the positive direction of y-axis is downwards. The given coordinate of game objects is at the top left corner of the object, not at the middle of it.

### Game Area

200 \* 500 pixels

### Game Objects

#### Ball

* The ball is a 5-by-5-pixel blue square.
* The moving speed is (&plusmn;7, &plusmn;7) pixels per frame.
* The ball is served from the platform, and it can be served to the left or right. If the ball is not served in 150 frames, it will be automatically served to the random direction.

#### Platform

* The platform is a 40-by-5-pixel green rectangle.
* The moving speed is (&plusmn;5, 0) pixels per frame.
* The initial position is at (75, 400).

#### Ball Slicing Mechanism

The x speed of the ball can be changed while caught by the platform:

* If the platform moves in the same direction of the ball, the x speed of the ball is increased to &plusmn;10, which is a fast ball.
* If the platform is stable, the x speed of the ball is reset to &plusmn;7.
* If the platform moves in the opposite direction of the ball, the ball will be hit back to the direction where it comes from, and the x speed is &plusmn;7.

The mechanism is added on the `NORMAL` difficulty.

#### Brick

* The brick is a 25-by-10-pixel orange rectangle.
* Its position is decided by the level map file.

#### Hard Bricks

* The hard brick is similar to the normal brick, but its color is red.
* The hard brick can be broken by hitting it twice. If it is hit once, it will become a normal brick. But it can be broken by hitting it only once with the fast ball.

## Communicate with Game

View the example of the ml script in [`ml/ml_play_template.py`](ml/ml_play_template.py).

### Methods

Use `mlgame.communication.ml` module to communicate with the game process.

* `ml_ready()`: Inform the game process that ml process is ready.
* `recv_from_game()`: Receive an dictionary object storing the game information from the game process.
* `send_to_game(dict)`: Send an dictionary object storing the command to the game process.

### Communication Objects

The dictionary object is used as the communication object transporting between game and ml processes.

#### Scene Information

It's an dictionary object sent from the game process, and also an object to be pickled in the record file.

The keys and values of the scene information:

* `"frame"`: An integer, The number of the frame that this scene information is for
* `"status"`: A string. The game status at this frame. It's one of the following value:
    * `"GAME_ALIVE"`: The game is still going.
    * `"GAME_PASS"`: All the bricks are broken.
    * `"GAME_OVER"`: The platform can't catch the ball.
* `"ball"`: An `(x, y)` tuple. The position of the ball.
* `"platform"`: An `(x, y)` tuple. The position of the platform.
* `"bricks"`: A list storing the position of remaining normal bricks (including the hard bricks that are hit once). All elements are `(x, y)` tuples.
* `"hard_bricks"`: A list storing the position of remaining hard bricks. All elements are `(x, y)` tuples.
* `"command"`: A string. The command decided for this frame. This member is used for recording the game progress

#### Game Command

It's an dictionary object sent to the game process for controlling the movement of the platform.

The keys and values of the game command:

* `"frame"`: An integer. The number of frame that this game command is for. It should be the same as the frame of the scene information received.
* `"command"`: A string. The command for controlling the platform. It's one of the following value:
    * `"SERVE_TO_LEFT"`: Serve the ball to the left
    * `"SERVE_TO_RIGHT"`: Serve the ball to the right
    * `"MOVE_LEFT"`: Move the platform to the left
    * `"MOVE_RIGHT"`: Move the platform to the right
    * `"NONE"`: Do nothing

## Custom Level Map Files

You can define your own map file, put it in the `game/level_data/` directory, and give it an unique filename  `<level_id>.dat`.

In the file, each line has 3 numbers representing the x, y position and the type of brick. The first line is the offset of all bricks, and the following lines are the position of bricks. Therefore, the final position of a brick is its position plus the offset. The third value in the first line is always -1. The third values in the following lines specify the type of the bricks, which 0 is a normal brick and 1 is a hard brick. For example:
```
25 50 -1
10 0 0
35 10 0
60 20 1
```
This map file contains 3 bricks, and their positions are at (35, 50), (60, 60), (85, 70), respectively, and the third brick is a hard brick.

## About the Ball

If the ball hits into another game object or the wall, the ball will be squeezed out directly to the hitting surface of that game object or the wall instead of compensating the bouncing distance.

![Imgur](https://i.imgur.com/ouk3Jzh.png)
