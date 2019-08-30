# Change Log

The format is modified from [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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