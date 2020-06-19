# MLGame

A platform for applying machine learning algorithm to play pixel games

MLGame separates the machine learning part from the game core, which makes users easily apply codes to play the game. (Support non-python script as the client. Check [here](mlgame/crosslang/README.md) for more information.)

For the concept and the API of the MLGame, visit the [wiki page](https://github.com/LanKuDot/MLGame/wiki) of this repo (written in Traditional Chinese).

## Requirements

* Python 3.6+
* pygame==1.9.6
* Other machine learning libraries you needed

## Usage

```
$ python MLGame.py [options] <game> [game_params]
```

* `game`: The name of the game to be started. Use `-l` flag to list available games.
* `game_params`: The additional parameters for the game. Use `python MLGame.py <game> -h` to list game parameters of a game.
  * Note that all arguments after `<game>` will be collected to this paremeter
* functional options:
  * `--version`: Show the version number
  * `-h`: Show the help message
  * `-l`: List available games
* game execution options:
  * `-f FPS`: Specify the updating frequency of the game
  * `-m`: Play the game in the manual mode (as a normal game)
  * `-1`: Quit the game when the game is over or is passed. Otherwise, the game will restart automatically.
  * `-r`: Pickle the game progress (a list of "SceneInfo") to log files.
  * `-i SCRIPT [-i SCRIPT ...]`: Specify the script used in the machine learning mode. For multiple scripts, use this flag multiple times. The script must have class `MLPlay` and be put in the `games/<game>/ml/` directory.

**Game execution options must be specified before &lt;game&gt; arguments.** Use `python MLGame.py -h` for more information.

For example:

* List available games:
  ```
  $ python MLGame.py -l
  ```

* List game parameters of the game arkanoid:
  ```
  $ python MLGame.py arkanoid -h
  ```

* Play the game arkanoid level 3 in manual mode on easy difficulty with 45 fps
  ```
  $ python MLGame.py -m -f 45 arkanoid EASY 3
  ```

* Play the game arkanoid level 2 on normal difficulty, record the game progress, and specify the script ml_play_template.py

  ```
  $ python MLGame.py -r -i ml_play_template.py arkanoid NORMAL 2
  ```

## Machine Learning Mode

If `-m` flag is **not** specified, the game will execute in the machine learning mode. In the machine learning mode, the main process will generate two new processes, one is for executing the game core (called game process), the other one is for executing the machine learning code (called ml process). They use pipes to communicate with each other.

![Imgur](https://i.imgur.com/xrkYm46.png)

Scene information is an object (such as dictionary) that stores the game status and the position of gameobjects in the scene. Game command is an object that stores the command for controlling the gameobject (such as a platform). The format of the scene information and the command are defined by game.

Below is an overview of the relationship between executor and class.

### Executor and Class

The executor runs a loop for executing the game or the machine learning code, and invokes member functions of the game class or the `MLPlay` class for passing the received object to the function or sending the object returned from the function.

#### Game class

Here is a template of the game class:

```python
class Game:
    def __init__(self, game_param_1, game_param_2, ...):
        ...

    def update(self, command):
        ...

    def reset(self):
        ...

    def get_player_scene_info(self):
        ...

    def get_keyboard_command(self):
        ...
```

* `__init__(game_param_1, game_param_2, ...)`: The initialization of the game class. The game parameters specified in the command line will be passed to it.
* `update(command)`: Update the game according to the received command.
  * If it's a multiplayer game, commands received from different players will be collected into a list and pass the list to `command` parameter.
  * If there is no returned value from `update()`, the game keeps going. If a string `"RESET"` is returned, the executor will invoke `reset()` to reset the game for the next round. If a string `"QUIT"` is returned, the game will be exited.
* `reset()`: Reset the game.
* `get_player_scene_info()`: Get the scene information to be sent to the machine learning process.
* `get_keyboard_command()`: Get commands according to pressed keys. This function is used in the manual mode.
  * Its return value will be passed to `update()` directly, therefore, the format of the returned commands should be the same as the machine learning mode.

#### `MLPlay` class

Here is a template of the game class:

```python
class MLPlay:
    def __init__(self, init_arg_1, init_arg_2, ...):
        ...

    def update(self, scene_info):
        ...

    def reset():
        ...
```

* `__init__(init_arg_1, init_arg_2, ...)`: The initialization of `MLPlay` class. The initial arguments sent from the game will be passed to it.
* `update(scene_info)`: Generate the game command according to the received scene information.
  * The format of game command is defined by the game.
  * If the returned value is a string `"RESET"`, `reset()` will be invoked.
* `reset()`: Do reset stuffs.

#### Execution Order

![Imgur](https://i.imgur.com/Ye3llUy.png)

The yellow blocks are the member functions of the game class or the `MLPlay` class which are invoked by the executor. Note that the game executor won't wait for the ml executor (except for the initialization or the resetting). Therefore, if the ml executor cannot send a game command in time, the command will be consumed in the next frame in the game executor, which is "delayed". Futhermore, when the game is over, the returned scene information must contain the game over status for the `MLPlay` class to inform the ml executor to reset.

The example script for the `MLPlay` class is in the file `games/<game>/ml/ml_play_template.py`, which is a class that simply returns the same command in `update()`.

### Non-python Client Support

MLGame supports that a non-python script runs as a ml client. For the supported programming languages and how to use it, please view the [README](mlgame/crosslang/README.md) of the `mlgame.crosslang` module.

## Log Game Progress

If `-r` flag is specified, the game progress will be logged into a file. When a game round is ended, the game progress is dumped to a file `<prefix>_<timestamp>.pickle` by using `pickle.dump()`. The prefix of the filename contains the game mode and game parameters, such as `ml_EASY_2_<timestamp>.pickle`. The file is saved in `games/<game>/log/` directory. These log files can be used to train the model.

### Format

The dumped game progress is a dictionary with two keys. The first key is `"scene_info"` whose value is a list of scene informations sent from the game process. The second key is `"command"` whose value is a list of commands sent from the ml process, but the last element of it is always `None` (Because there is no command to be sent when the game is over). If the game is a multiplayer game, each element in the list of the `"command"` is a list storing the commands returned by different players.

The game progress of the single player game will be like:

```
{
    "scene_info": [scene_info_0, scene_info_1, ... , scene_info_n-1, scene_info_n],
    "command": [command_0, command_1, ... , command_n-1, None]
}
```

And the multiplayer game:

```
{
    "scene_info": [scene_info_0, scene_info_1, ... , scene_info_n-1, scene_info_n],
    "command": [[command_1P_0, command_2P_0], ... , [command_1P_n-1, command_2P_n-1], None]
}
```

### Read Game Progress

You can use `pickle.load()` to read the game progress from the file.

Here is the example for read the game progress:

```python
import pickle
import random

def print_log():
    with open("path/to/log/file", "rb") as f:
        p = pickle.load(f)

    random_id = random.randrange(len(p))
    print("Scene information:", p["scene_info"][p])
    print("Command:", p["command"][p])

if __name__ == "__main__":
    print_log()
```

For the non-python client, it may need to write a python script to read the record file and convert the game progess to other format (such as plain text) for the non-python client to read.

### Access Trained Data

The ml script needs to load the trained data from external files. It is recommended that put these files in the same directory of the ml script and use absolute path to access them.

For example, there are two files `ml_play.py` and `trained_data.sav` in the same ml directory:

```python
import os.path
import pickle

def ml_loop():
    dir_path = os.path.dirname(__file__)  # Get the absolute path of the directory of this file in
    data_file_path = os.path.join(dir_path, "trained_data.sav")

    with open(data_file_path, "rb") as f:
        data = pickle.load(f)
```

## Change Log

View [CHANGELOG.md](./CHANGELOG.md)

## README of the Game

* [arkanoid](games/arkanoid/README.md)
* [pingpong](games/pingpong/README.md)
* [snake](games/snake/README.md)
