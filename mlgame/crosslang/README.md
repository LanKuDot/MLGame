# `mlgame.crosslang` package

The package supporting the execution of non-python ml client.

## How It Works

### ML Scripts

The non-python script for the ml client is placed in the `ml` directory of the game, which is the same as the python script.

### Compilation

<img src="https://i.imgur.com/XbOCnVG.png" width="500px" />

If the user specifies a non-python script, MLGame will invoke `mlgame.crosslang.main` module to handle the script. `mlgame.crosslang.main` module will check the file extension of the script, and find corresponding programming language in `EXTENSION_LANG_MAP`. Then, it will invoke the module `mlgame.crosslang.compile.<lang>` to compile the script. For example, if the user specifies `ml_play.cpp`, the `mlgame.crosslang.compile.cpp` module is used. The language compliation module will preprocess the script, link libraries, compile, and return the execution command in a list object.

### Execution

<img src="https://i.imgur.com/eLqOe9Y.png" width="600px" />

After compilation, `mlgame.crosslang.ml_play` module runs in the ml process. It summons a subprocess to execute command, and runs as communication bridge between the game and the non-python client. The I/O of the client is redirected to the module, therefore, the client can receive and send messages via basic I/O. For example, `std::cout` and `std::cin` for C++.

#### Message Format

The communication message between the client and the module is always a JSON string with a header string:
* The message sent to the client:
    * Initial arguments: `"__init__ {"args": [...], "kwargs": {...}}\n"`
    * Scene information: `"__scene_info__ <scene_info_in_JSON_str>\n"`. `scene_info` is a dictionary object sent from the game.
* The message received from the client:
    * Ready command: `"__command__ READY\n"`
    * Game command: `"__command__ <game_command_in_JSON_str>\n"`. The `game_command_in_JSON_str` will be decoded to a dictionary object and be sent to the game.

The message received from the client without `"__command__"` header will be printed out directly.

**&gt;&gt;&gt; Important! &lt;&lt;&lt;** All the message sent from the client must contain a newline character ("\n") at the end. And then flush the message from stdout each time, otherwise, the message will be left in the buffer, and the moudle won't receive it until the buffer is full. For example, in C++, always use `std::endl` at the end of `std::cout`, which will add a newline character and flush the message.

#### Client API

The client API for the target language helps to convert the message format listed above to the usable object, and vice versa. There are 4 functions to be implemented:

* `get_init_args()`: Get the initial arguments. It will return an usable object.
* `get_scene_info()`: Get the scene information from the game. It will return an usable object.
* `ml_ready()`: Send the ready command to the game.
* `send_command(command)`: Send the game command to the game. `command` parameter will get an usable object which will be converted to JSON string in the function.

#### Interaction Flow

Here is the interaction flow between MLGame and the non-python sctipt:

<img src="https://i.imgur.com/UYtxvHu.png" width="650px" />

## Supported Language

This section list supported languages and examples. Additional libraries may be needed to run the script. Follow instructions below to set up libraries of the target language.

### C++

The code is compiled with flag `--std=c++11`. A `ml_play.out` file is generated in the same directory of the code after compilation for execution.

#### Additional Libraries

1. Download the `json.hpp` file from https://github.com/nlohmann/json/releases (in the "Assets" section of the release version choiced).
2. Put `json.hpp` in `mlgame/crosslang/compile/include/cpp/` directory.

#### Exapmle

The API is defined in [`mlgame_client.hpp`](./compile/include/cpp/mlgame_client.hpp), and it will be included in a predefined main code [`base_main.cpp`](./compile/include/cpp/base_main.cpp). User only need to start from implementing the `ml_loop()` function. The user script will be appended to `base_main.cpp` before compliation.

```c++
void ml_loop(json init_args)
{
    cout << init_args["args"] << " " << init_args["kwargs"] << endl;
    ml_ready();

    while (1) {
        json scene_info = get_scene_info();
        json command;

        /* Inform the game that it's ready for the next round. */
        if (scene_info["status"] == "GAME_OVER") {
            ml_ready();
            continue;
        }

        command["frame"] = scene_info["frame"];
        command["command"] = "MOVE_LEFT";
        send_command(command);
    }
}
```
