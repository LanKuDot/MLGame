# `mlgame.crosslang` package

The package supporting the execution of non-python ml client.

The scene information sent from the game is converted to json string by [`json.dumps()`](https://docs.python.org/3/library/json.html#json.dumps) and the game command sent back to the game is converted to python object from json string by [`json.loads()`](https://docs.python.org/3/library/json.html#json.loads). The client API will convert json string to an usable object for the script to use, and vice versa.

For the documenation and how to support another language, please visit [DOCUMENTATION.md](./DOCUMENTATION.md)

## Supported Language

This section list supported languages and examples. Additional libraries may be needed to run the script. Follow instructions below to set up libraries of the target language.

### C++

The code is compiled with flag `--std=c++11`. A `ml_play.out` file is generated in the same directory of the code after compilation for execution.

#### Additional Libraries

1. Download the `json.hpp` file from https://github.com/nlohmann/json/releases (in the "Assets" section of the release version choiced).
2. Put `json.hpp` in `mlgame/crosslang/compile/cpp/include/` directory.

**`json` how to**

The json string received from the game will be converted to a `json` object, or a `json` object will be converted to a json string.

Here is an example scene information in json string:

```json
{
    "status": "GAME_ALIVE",
    "ball": [[1, 2], [3, 4]]
}
```

The corresponding `json` object will be:

```c++
json update(json scene_info)
{
    cout << scene_info["status"] << endl;       // "GAME_ALIVE"
    cout << scene_info["ball"][0][0] << " "
        << scene_info["ball"][0][1] << endl;    // 1 2
}
```

The json string can be generated from a `json` object:

```c++
json j;

j["direction"] = "LEFT";
j["action"] = "SPEED_UP";
j["data"] = {1, 2, 3};      // An array is stored as std::vector
```

The corresponding json string will be:

```json
{
    "direction": "LEFT",
    "action": "SPEED_UP",
    "data": [1, 2, 3]
}
```

If the game command is just a string, add it to `json` object directly:

```c++
json j = "TURN_LEFT";
```

For more examples view: https://github.com/nlohmann/json#examples

#### class `MLPlay`

The user script must provide class `MLPlay`. `MLPlay` should be derived from `AbstractMLPlay` which is defined in [`ml_play.hpp`](./compile/cpp/include/ml_play.hpp). Here are member functions:
- `MLPlay(json init_args)`: Initialize the `MLPlay`.
    - `init_args`: The initial arguments sent from the game. Access the positional arguments by `init_args["args"][index]` or the keyword arguments by `init_args["kwargs"][name]`.
- `json update(json scene_info) override`: Received the scene information sent from the game and generate the game command. Both data are stored in a `json` object.
- `void reset() override`: Reset the `MLPlay`. This function is called when `update()` returns `"RESET"` if the game is over.

#### Example

Here is an example for play game `arkanoid`:

```c++
#include <iostream>
#include <ml_play.hpp>

using namespace std;

class MLPlay : public AbstractMLPlay
{
public:
    bool is_ball_served = false;

    // The constructor must have 1 parameter "init_args"
    // for passing initial arguments
    MLPlay(json init_args)
    {
        cout << init_args << endl;
    }

    json update(json scene_info) override
    {
        json command;

        if (scene_info["status"] == "GAME_OVER" ||
            scene_info["status"] == "GAME_PASS") {
            command = "RESET";   // "RESET" command
            return command;
        }

        if (!this->is_ball_served) {
            command = "SERVE_TO_LEFT";
            this->is_ball_served = true;
        } else
            command = "MOVE_LEFT";

        return command;
    }

    void reset() override
    {
        this->is_ball_served = false;
    }
};
```
