# `mlgame.crosslang` package

The package supporting the execution of non-python ml client.

## How It Works

### ML Scripts

The non-python script for the ml client is placed in the `ml` directory of the game, which is the same as the python script.

### Compilation

<img src="https://i.imgur.com/EwFF9ct.png" width="450px" />

If the user specifies a non-python script, MLGame will invoke `mlgame.crosslang.main` module to handle the script. `mlgame.crosslang.main` module will check the file extension of the script, and find corresponding programming language in `EXTENSION_LANG_MAP`. Then, it will invoke `compile_script()` defined in the module `mlgame.crosslang.compile.<lang>.main` to compile the script. For example, if the user specifies `ml_play.cpp`, the `mlgame.crosslang.compile.cpp.main` module is used. The full path of the non-python script is passed to the `compile_script()`, and then the function will preprocess the script, link libraries, compile, and return the execution command in a list object.

### Execution

<img src="https://i.imgur.com/eLqOe9Y.png" width="600px" />

After compilation, `mlgame.crosslang.ml_play` module runs in the ml process. It summons a subprocess to execute command, and runs as communication bridge between the game and the non-python client. The I/O of the client is redirected to the module, therefore, the client can receive and send messages via basic I/O. For example, `std::cout` and `std::cin` for C++.

#### Message Format

The communication message between the client and the module is always a JSON string with a header string (But ready and reset command is just a string):
* The message sent to the client:
    * Initial arguments: `"__init__ {"args": [...], "kwargs": {...}}\n"`
    * Scene information: `"__scene_info__ <scene_info_in_JSON_str>\n"`. `scene_info` is a dictionary object sent from the game.
* The message received from the client:
    * Ready command: `"__command__ READY\n"`
    * Reset command: `"__command__ RESET\n"`
    * Game command: `"__command__ <game_command_in_JSON_str>\n"`. The `game_command_in_JSON_str` will be decoded to python object by using `json.loads()` and be sent to the game.

The message received from the client without `"__command__"` header will be printed out directly.

**&gt;&gt;&gt; Important! &lt;&lt;&lt;** All the message sent from the client must contain a newline character ("\n") at the end. And then flush the message from stdout each time, otherwise, the message will be left in the buffer, and the moudle won't receive it until the buffer is full. For example, in C++, always use `std::endl` at the end of `std::cout`, which will add a newline character and flush the message.

#### Communication API

The communication API for the target language helps to convert the message format listed above to the usable object, and vice versa. There are 5 functions to be implemented:

* `get_init_args()`: Get the initial arguments. It will return an usable object.
* `get_scene_info()`: Get the scene information from the game. It will return an usable object.
* `client_ready()`: Send the ready command to the game.
* `client_reset()`: Send the reset command to the game.
* `send_command(command)`: Send the game command to the game. `command` parameter will get an usable object which will be converted to JSON string in the function.

#### Interaction Flow

Here is the interaction flow between MLGame and the communication API:

<img src="https://i.imgur.com/VS84oB6.png" width="650px" />

When the game ends, the communication API has to send the "RESET" command:

<img src="https://i.imgur.com/k5lLgnd.png" width="650px" />

#### Simulate `MLPlay`

You could provide the API like `MLPlay` to the user, and write a loop to interact with communication API and user's `MLPlay`. There are 3 member functions of `MLPlay`:

* `constructor(init_args)`: Do initialization jobs. `init_args` is the initial arguments sent from the game.
* `update(scene_info) -> [game|reset]command`: Handle the scene information and generate the command. The returned command could be game command or the reset command.
* `reset()`: Do reset jobs.

The flow of communication API and the user's `MLPlay`:

<img src="https://i.imgur.com/UmYSKQg.png" />

Check the [`base_main.cpp`](./compile/cpp/include/base_main.cpp) of C++ library for the example.

## Supported Language

This section list supported languages and examples. Additional libraries may be needed to run the script. Follow instructions below to set up libraries of the target language.

### C++

The code is compiled with flag `--std=c++11`. A `ml_play.out` file is generated in the same directory of the code after compilation for execution.

#### Additional Libraries

1. Download the `json.hpp` file from https://github.com/nlohmann/json/releases (in the "Assets" section of the release version choiced).
2. Put `json.hpp` in `mlgame/crosslang/compile/cpp/include/` directory.

#### Exapmle

The user API is defined in [`ml_play.hpp`](./compile/cpp/include/ml_play.hpp). The user script will be included in the [`base_main.cpp`](./compile/cpp/include/base_main.cpp) for execution.

```c++
#include <iostream>
#include <ml_play.hpp>

using namespace std;

class MLPlay : public AbstractMLPlay
{
public:
    bool is_ball_served;

    // The constructor must have 1 parameter "init_args" for passing initial arguments
    MLPlay(json init_args)
    {
        this -> is_ball_served = false;
        cout << init_args << endl;
    }

    json update(json scene_info)
    {
        json command;

        if (scene_info["status"] == "GAME_OVER" ||
            scene_info["status"] == "GAME_PASS") {
            command = "RESET";   // "RESET" command
            return command;
        }

        if (!this -> is_ball_served) {
            command = "SERVE_TO_LEFT";
            this -> is_ball_served = true;
        } else
            command = "MOVE_LEFT";

        return command;
    }

    void reset()
    {
        this -> is_ball_served = false;
    }
};
```
