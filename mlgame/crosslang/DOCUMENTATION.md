# Documentation of `crosslang` Module

## Table of Contents

* [How It Works](#how-it-works)
    * [ML Scripts](#ml-scripts)
    * [Compilation](#compilation)
    * [Execution](#execution)
* [How to Support Another Language](#how-to-support-another-language)
    * [Generate Execution Command](#generate-execution-command)
    * [Language API](#language-api)

## How It Works

### ML Scripts

The non-python script for the ml client is also placed in the `ml` directory of the game.

### Compilation

<img src="https://i.imgur.com/EwFF9ct.png" width="450px" />

If the user specifies a non-python script, MLGame will:
1. Invoke `mlgame.crosslang.main` module to handle the script.
2. `mlgame.crosslang.main` module will check the file extension of the script, and find corresponding programming language `lang` in `EXTENSION_LANG_MAP` defined in `ext_lang.map.py`.
3. Invoke `compile_script()` defined in the module `mlgame.crosslang.compile.<lang>.main` to compile the script. For example, if the user specifies `ml_play.cpp`, the `mlgame.crosslang.compile.cpp.main` module is used.
4. The full path of the non-python script is passed to the `compile_script()`, and then the function will preprocess the script, link libraries, compile, and return the execution command in a list object.

### Execution

<img src="https://i.imgur.com/eLqOe9Y.png" width="600px" />

After compilation, `mlgame.crosslang.ml_play` module runs in the ml process as the proxy of the non-python client. It summons a subprocess to execute the client, and runs as communication bridge between the game and the client. The I/O of the client is redirected to the module, therefore, the client can receive and send messages via basic I/O. For example, `std::cout` and `std::cin` for C++.

The message sent between the module and the client is a header string following a JSON string. The language API handles the message and convert it to the usable object for the user program to execute.

## How to Support Another Language

### Generate Execution Command

1. Create a directory in `mlgame/crosslang/compile` and name it to the language name
2. Create `__init__.py` and `main.py` in the new directory
3. Edit `main.py` with the following code:

```python
from pathlib import Path
from mlgame.crosslang.exceptions import CompilationError

def compile_script(script_full_path):

    # Code for handling the source code #

    # Raise CompilationError if an error occurred
    if error_occurred:
        raise CompilationError(Path(script_full_path).name, reason)

    # Generate the execution command stored in a list object #
    # A word is an element. For example, ["command", "path/to/file", "--foo", "--bar"] #
    return [excution_cmd]
```
The method `compile_script` is used for handling the source code, and `script_full_path` is a string storing the full path to the code. If it will generate additional files, it is recommended that put them in the same directory as the source code. The returned object is a list storing the execution command.

4. Edit `mlgame/crosslang/ext_lang_map.py` and add the "file extension-language" pair (".js": "javascript" for example) to the dictionary `EXTENSION_LANG_MAP`

### Language API

The language API provides an interface for the user to get the object sent from the game or send the object back to the game. The object will be converted to the string format and it will be sent or received via standard I/O. The string format is a header string following a JSON string.

#### Methods

There are 5 functions to be implemented:

**Get the object sent from the game**

* `get_init_args()`: Get the initial arguments. It will return an usable object.
    * Received string format: `"__init__ {"args": [...], "kwargs": {...}}\n"`
* `get_scene_info()`: Get the scene information from the game. It will return an usable object.
    * Received string format: `"__scene_info__ <scene_info_in_JSON_str>\n"`. `scene_info` is a dictionary object sent from the game.

For example:
```c++
json get_scene_info()
{
    string scene_info_str;
    getline(cin, scene_info_str);

    // Ignore header "__scene_info__"
    scene_info_str.erase(0, scene_info_str.find_first_of('{'));

    return json::parse(scene_info_str);
}
```

**Send the object back to the game**

* `client_ready()`: Send the ready command to the game.
    * Sent string format: `"__command__ READY\n"`
* `client_reset()`: Send the reset command to the game.
    * Sent string format: `"__command__ RESET\n"`
* `send_command(command)`: Send the game command to the game. `command` parameter will get an usable object which will be converted to JSON string in the function.
    * Sent string format: `"__command__ <game_command_in_JSON_str>\n"`.

For example:
```c++
void client_reset()
{
    cout << "__command__ RESET" << endl;
}
```

The message received from the client without `"__command__"` header will be printed out directly.

**&gt;&gt;&gt; Important! &lt;&lt;&lt;** All the message sent from the client must contain a newline character ("\n") at the end. And then flush the message from stdout each time, otherwise, the message will be left in the buffer, and the moudle won't receive it until the buffer is full. For example, in C++, always use `std::endl` at the end of `std::cout`, which will add a newline character and flush the message.

#### Simulate `MLPlay`

You could provide a class like `MLPlay` to the user, and write a loop to interact with language API and user's `MLPlay`. There are 3 member functions of `MLPlay`:

* `constructor(init_args)`: Do initialization jobs. `init_args` is the initial arguments sent from the game.
* `update(scene_info) -> [game|reset]command`: Handle the scene information and generate the command.
    * The returned command could be game command or the reset command (could be a `"RESET"` for example)
* `reset()`: Do reset jobs.

The flow chart of the loop:

<img src="https://i.imgur.com/OdcVDyn.png" />

For example:
```c++
int main()
{
    AbstractMLPlay *ml = new MLPlay(get_init_args());
    client_ready();

    json command;
    while (1) {
        command = ml->update(get_scene_info());
        if (command == "RESET") {
            client_reset();
            ml->reset();
            client_ready();
            continue;
        }
        send_command(command);
    }

    delete ml;
    return 0;
}
```
