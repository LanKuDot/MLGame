# `mlgame.crosslang` package

The package supporting the execution of non-python ml client.

For the documenation and how to support another language, please visit [DOCUMENTATION.md](./DOCUMENTATION.md)

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

    json update(json scene_info) override
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

    void reset() override
    {
        this -> is_ball_served = false;
    }
};
```
