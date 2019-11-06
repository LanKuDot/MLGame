# Arkanoid

<img src="https://i.imgur.com/2b35CWu.gif" height="500"/>

## Execution

* Manual mode: `python MLGame.py arkanoid [level_id] -m`
    * Controlling: ก๖, ก๗
* ML mode: `python MLGame.py arkanoid [level_id] -i ml_play_template.py`

`[level_id]` is used to specify the level map. If it is not specified, it will be 1. The available `[level_id]` can be checked in `game/level_data/` directory.

## Overview

### Game Area

200 \* 500 pixels

### Game Objects

#### Ball

* The ball is a 5-by-5-pixel blue square.
* The moving speed is (กำ7, กำ7) pixels per frame.
* The initial position is at (100, 100), and it moves toward the lower right.

#### Platform

* The platform is a 40-by-5-pixel green rectangle.
* The moving speed is (กำ5, 0) pixels per frame.
* The initial position is at (75, 400).

#### Brick

* The brick is a 25-by-10-pixel orange rectangle.
* Its position is decided by the level map file.

### Game Status

* `GAME_PASS`: All bricks are destroyed.
* `GAME_OVER`: The ball is below the platform.

## Communicate with Game

View the example of the ml script in [`ml/ml_play_template.py`](ml/ml_play_template.py).

### Data Structures

#### `SceneInfo`

Store the information of the scene. Defined in [`game/gamecore.py`](game/gamecore.py).

The members of the `SceneInfo`:

* `frame`: The number of the frame that this `SceneInfo` is for
* `status`: The game status at this frame. It's one of `GameStatus`.
* `ball`: The position of the ball. It's a `(x, y)` tuple.
* `platform`: The position of the platform. It's a `(x, y)` tuple.
* `bricks`: A list storing the position of remaining bricks. All elements are `(x, y)` tuples.
* `command`: The command decided for this frame. It's one of `PlatformAction`. This member is used for recording the game progress

#### `GameStatus`

The game status. Defined in [`game/gamecore.py`](game/gamecore.py).

There are 3 `GameStatus`: `GAME_ALIVE`, `GAME_PASS`, and `GAME_OVER`. `GAME_ALIVE` means that the game is still going.

#### `PlatformAction`

Control the movement of the platform. Defined in [`game/gameobject.py`](game/gameobject.py).

There are 3 `PlatformAction`: `MOVE_LEFT`, `MOVE_RIGHT`, and `NONE`.

### Methods

The following methods are defined in [`communication.py`](communication.py).

* `ml_ready()`: Inform the game process that ml process is ready.
* `get_scene_info()`: Receive the `SceneInfo` sent from the game process.
* `send_instruction(frame, command)`: Send the command to the game process.
    * `frame`: The number of frame that this command is for. This value should be the same as the `frame` of the received `SceneInfo`.
    * `command`: The command for controlling the platform. It's one of `PlatformAction`.

## Level Map Files

The level map files are in the `game/level_data/` directory, and the filename is `<level_id>.dat`.

In the file, each line is a pair of numbers representing the x and y position. The first line is the offset of all bricks, and the following lines are the position of bricks. Therefore, the final position of a brick is its position plus the offset. For example:
```
25 50
10 0
35 10
60 20
```
This map file contains 3 bricks, and their positions are at (35, 50), (60, 60), (85, 70), respectively.

You can define your own map file, put it in the `game/level_data/` directory, and give it an unique `level_id`.

## About the Ball

If the ball hits into another game object or the wall, the ball will be squeezed out directly to the hitting surface of that game object or the wall instead of compensating the bouncing distance.

![Imgur](https://i.imgur.com/ouk3Jzh.png)
