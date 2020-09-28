from .ext_lang_map import EXTESION_LANG_MAP

import importlib
import os.path

def compile_script(script_full_path):
    """
    Compile the script to an executable according to its file extension

    This function will load the corresponding language module according to
    `EXTENSION_LANG_MAP` for compiling the script.

    @param script_full_path The full path of the target script
    @return A list of command segments for executing the executable
    """
    path_no_ext, extension = os.path.splitext(script_full_path)
    compilation_module = importlib.import_module(
        ".compile.{}.main".format(EXTESION_LANG_MAP[extension]), __package__)

    script_execution_cmd = compilation_module.compile_script(script_full_path)
    if not isinstance(script_execution_cmd, list):
        raise TypeError("The returned execution command is not a list.")

    return script_execution_cmd
