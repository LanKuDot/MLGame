# MLGame

A platform for applying machine learning algorithm to play pixel games

MLGame separates the machine learning part from the game core, which makes users easily apply codes to play the game.

**MLGame Beta 4.0+ is not compatible with the previous version.**

## Requirements

* Python 3.5+
* pygame==1.9.4
* Other machine learning libraries you needed

## Usage

```
$ python MLGame.py [options] <game> [game_params]
```

* `game`: The name of the game to be started. Available games are "arkanoid" and "pingpong"
* `game_params`: The additional parameters for the game.
* `options`:
  * `-f FPS`: Specify the updating frequency of the game
  * `-m`: Play the game in the manual mode (as a normal game)
  * `-1`: Quit the game when the game is over or is passed. Otherwise, the game will restart automatically.
  * `-r`: Pickle the game progress (a list of `SceneInfo`) to log files.
  * `-i SCRIPT [SCRIPT ...]`: Specify the script(s) used in the machine learning mode. The script must have function `ml_loop()` and be put in the `games/<game>/ml/` directory.

Use `python MLGame.py -h` for more information. Note that `-i` flag and the following "SCRIPTs" should be placed at the end of the command.

For example:

* Play the game arkanoid level 3 in manual mode with 45 fps
  ```
  $ python MLGame.py -m -f 45 arkanoid 3
  ```

* Play the game arkanoid level 2, record the game progress, and specify the script ml_play_template.py

  ```
  $ python MLGame.py -r arkanoid 2 -i ml_play_template.py
  ```

## Machine Learning Mode

If `-m` flag is **not** specified, the game will execute in the machine learning mode. In the machine learning mode, the main process will generate two new processes, one is for executing the machine learning code (called ml process), the other is for executing the game core (called game process). They use pipes to communicate with each other.

![](https://i.imgur.com/Wlai4Bh.png)

`SceneInfo` is the data structure that stores the game status and the position of gameobjects in the scene. `GameInstruction` is the data structure that stores the command for controlling the gameobject (such as a platform). Both are defined in the file `games/<game>/communication.py`.

### Execution Order

![](https://i.imgur.com/D3D5Mm3.png)

Note that the game process won't wait for the ml process. Therefore, if the ml process cannot send a `GameInstruction` in time, the instruction will be consumed in the next frame in the game process, which is "delayed".

The example script for the ml process is in the file `<game>/ml/ml_play_template.py`, which is a script that simply sent a "moving left" command to the game process. There are detailed comments in the script to describe how to write your own script.

## Log Game Progress

if `-r` flag is specified, the game progress will be logged into a file. When a game round is ended, a list of `SceneInfo` is dumped to a file `<timestamp>.pickle` by using `pickle.dump()`. The file is saved in `games/<game>/log/` directory. These log files can be used to train the model.

## Change Log

View [CHANGELOG.md](./CHANGELOG.md)

## External Links

Documentation for the gamecore (written in Traditional Chinese)
* [arkanoid](https://hackmd.io/s/HkaT0SZH4)
* [pingpong](https://hackmd.io/s/SJnGAPdjN)
