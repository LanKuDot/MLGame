# Change Log

The format is modified from [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

### [Beta 7.1.3] - 2020.06.20

**Fixed**

* Handle the exception of `SystemExit`
* Handle the situation of reseting the ml executor before the game ends
  * The game executor will ignore the ready command.

**Changed**

* Optimize the checking of the received object from either side

### [Beta 7.1.2] - 2020.06.19

**Fixed**

* Use wrong value to chack frame delay

**Changed**

* Modify the game "snake" for the game development tutorial
  * The `ml_play_template.py` of the game "snake" contains simple rule-based algorithm.

### [Beta 7.1.1] - 2020.06.15

**Changed**

* ML process doesn't send the command only when the returned value of `MLPlay.update()` is `None`.

### [Beta 7.1] - 2020.06.01

**Fixed**

* Handle the exception of `BrokenPipeError`

**Added**

* Add "dynamic_ml_clients" to the "GAME_SETUP" of the game config

### [Beta 7.0.1] - 2020.05.29

This update is compatible with Beta 7.0.

**Fixed**

* Hang when the game exits on Linux

**Added**

* Add `errno.py` to define the exit code of errors
* Handle the exception occurred in manual mode

**Changed**

* Change the exit code of errors

### [Beta 7.0] - 2020.05.27

**Added**

* Use executors to control the execution loop
  * The game and the ml script only need to provide "class" for the executor to invoke (like an interface).
  * The game doesn't need to provide manual and ml version. Just one game class.
  * Replace `ml_loop()` with `MLPlay` class in ml script
* Add commnuication manager
  * The manager for the ml process has a queue for storing the object received. If the queue has more than 15 objects, the oldest object will be dropped.

**Changed**

* Change the format of the recording game progress
* Replace `PROCESSES` with `GAME_SETUP` in `config.py` of the game to setup the game and the ml scripts
* Rename `GameConfig` to `ExecutionCommand`
* Simplfy the `communication` package into a module

**Removed**

* Remove `record.py` and ml version of the game in the game directory

### [Beta 6.1] - 2020.05.06

**Changed**

* Pingpong - version 1.1
  * Shorten the ball speed increasing interval
  * Randomly set the initial position of the blocker, and speed up the moving speed of it

### [Beta 6.0] - 2020.04.28

**Added**

* Add `-l` and `--list` flag for listing available games
* Use `config.py` in games to set up the game parameters and the game execution
* Use `argparse` for generating and handling game parameters
  * List game parameters of a game by using `python MLGame.py <game> -h`
* Exit with non-zero value when an error occurred

**Changed**

* The game execution flags must be specified before the game name, including `-i/--input-script/--input-module` flags
* `-i/--input-script/--input-module` flags carry one script or one module at a time.
  * Specify these flags multiple times for multiple scripts or modules, such as `-i script_1P -i script_2P`.
* Games: Use dictionary objects as communication objects between game and ml processes for flexibility
  * The record file only contains dictionay objects and built-in types, therefore, it can be read outside the `mlgame` directory.
* `mlgame.gamedev.recorder.RecorderHelper` only accepts dictionary object.
* Code refactoring

**Removed**

* Games
  * Remove `main.py` (replaced by `config.py`)
  * Remove `communication.py`
    * For the ml script, use `mlgame.communication.ml` module to communicate with the game process. See `ml_play_template.py` for the example.
* Remove `CommandReceiver` from the `mlgame.communication.game`
  * The game has to validate the command recevied by itself.

### [Beta 5.0.1] - 2020.03.06

**Fixed**

* Fix typo in the README of the arkanoid
* Arkanoid: Add additional checking condition for the ball bouncing

### [Beta 5.0] - 2020.03.03

**Added**

* Arkanoid and Pingpong:
  * The serving position and direction of the ball can be decided
  * Add difficulties for different mechanisms
  * Add ball slicing mechanism
* Arkanoid: Add hard bricks
* Pingpong: Add blocker

**Changed**

* Update the python from 3.5 to 3.6: For the `auto()` of the custom `Enum`
* Optimize the output of the error message
* Refactor the game classes: Extract the drawing and recording functions
* Add prefix to the filename of the record files
* Physics: Optimize the ball bouncing algorithm

### [Beta 4.1] - 2019.11.06

**Added**

* New game - Snake
* Add README to the game Arkanoid and Pingpong

**Changed**

* Update pygame from 1.9.4 to 1.9.6
* Arkanoid and Pingpong (Follow the structure of the game Snake):
  * Move `SceneInfo` to the `gamecore.py`
  * Rename `GameInstruction` to `GameCommand`
* Arkanoid: Add `command` member to `SceneInfo`
  * Trying to load the record files generated before beta 4.1 will get `AttributeError: 'SceneInfo' object has no attribute 'command'` error.
* Code refactoring

### [Beta 4.0] - 2019.08.30

**Added**

* `mlgame` - MLGame development API
* `--input-module` flag for specifying the absolute importing path of user modules

**Changed**

* Use 4 spaces instead of tab
* Support one shot mode in the manual mode
* Fit the existing games to the new API
* Move the directory of game to "games" directory
* Arkanoid: Wait for the ml process before start new round
* Arkanoid: Change the communication API

### [Beta 3.2] - 2019.07.30

**Changed**

* Pingpong: Exchange the 1P and 2P side
* Code refactoring

### [Beta 3.1] - 2019.05.28

**Changed**

* Pingpong: Set the height of the platform from 10 to 30
* Optimize the collision detection algorithm

### [Beta 3.0] - 2019.05.22

**Added**

* 2P game "pingpong"

**Changed**

* Optimize the call stack message of ml process
* Use `argparse` instead of `optparse`

### [Beta 2.2.2] - 2019.04.15

**Fixed**

* The game doesn't wait for the ready command

### [Beta 2.2.1] - 2019.04.12

**Fixed**

* The game hangs when the exception occurred before `ml_ready()`

**Changed**

* Some code refactoring and optimization

### [Beta 2.2] - 2019.04.01

**Added**

* `-i` and `--input-script` for specifying the custom ml script

### [Beta 2.1.1] - 2019.03.21

**Added**

* Print the whole call stack when the exception occurred

### [Beta 2.1] - 2019.03.18

**Fixed**

* Quit the game automatically when an exception occurred

**Added**

* `-1` and `--one-shot` for the one shot mode in ml mode
* Version message

### [Beta 2.0] - 2019.02.27

**Changed**

* Use function call instead of class instance to invoke use code
* Optimize the collision detection algorithm
* Increase the difficulty of the game "arkanoid"

**Added**

* `-r` and `--record` to record the game progress
