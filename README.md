# MLGame

A platform for applying machine learning algorithm to play pixel games

MLGame separates the machine learning part from the game core, which makes users easily apply codes to play the game.

**MLGame Beta 6.0+ is not compatible with the previous version.**

## Requirements

* Python 3.6+
* pygame==1.9.6
* Other machine learning libraries you needed

## Usage

```
$ python MLGame.py [options] <game> [game_params] [-i SCRIPT(S)]
```

* `game`: The name of the game to be started. Use `-l` flag to list available games.
* `game_params`: The additional parameters for the game. Use `python MLGame.py <game> -h` to list game parameters of a game.
* `function options`:
  * `--version`: Show the version number
  * `-h`: Show the help message
  * `-l`: List available games
* `game execution options`:
  * `-f FPS`: Specify the updating frequency of the game
  * `-m`: Play the game in the manual mode (as a normal game)
  * `-1`: Quit the game when the game is over or is passed. Otherwise, the game will restart automatically.
  * `-r`: Pickle the game progress (a list of `SceneInfo`) to log files.
  * `-i SCRIPT [SCRIPT ...]`: Specify the script(s) used in the machine learning mode. The script must have function `ml_loop()` and be put in the `games/<game>/ml/` directory.

Use `python MLGame.py -h` for more information. Note that `-i` flag and its following "SCRIPTs" should be placed at the end of the command.

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
  $ python MLGame.py arkanoid NORMAL 2 -r -i ml_play_template.py
  ```

## Machine Learning Mode

If `-m` flag is **not** specified, the game will execute in the machine learning mode. In the machine learning mode, the main process will generate two new processes, one is for executing the machine learning code (called ml process), the other is for executing the game core (called game process). They use pipes to communicate with each other.

![Imgur](https://i.imgur.com/ELXiFIZ.png)

"SceneInfo" is a dictionary object that stores the game status and the position of gameobjects in the scene. "GameCommand is also a dictionary object that stores the command for controlling the gameobject (such as a platform).

### Execution Order

![Imgur](https://i.imgur.com/t7itbDH.png)

Note that the game process won't wait for the ml process (except for the initialization). Therefore, if the ml process cannot send a "GameCommand" in time, the instruction will be consumed in the next frame in the game process, which is "delayed".

The example script for the ml process is in the file `games/<game>/ml/ml_play_template.py`, which is a script that simply sent the same command to the game process. There are detailed comments in the script to describe how to write your own script.

### Access trained data

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

## Log Game Progress

if `-r` flag is specified, the game progress will be logged into a file. When a game round is ended, a list of "SceneInfo" (i.e. a list of dictionay objects) is dumped to a file `<prefix>_<timestamp>.pickle` by using `pickle.dump()`. The prefix of the filename contains the game mode and game parameters, such as `ml_EASY_2_<timestamp>.pickle`. The file is saved in `games/<game>/log/` directory. These log files can be used to train the model.

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
    print(p[random_id])

if __name__ == "__main__":
    print_log()
```

## Change Log

View [CHANGELOG.md](./CHANGELOG.md)

## README of the Game

* [arkanoid](games/arkanoid/README.md)
* [pingpong](games/pingpong/README.md)
* [snake](games/snake/README.md)
