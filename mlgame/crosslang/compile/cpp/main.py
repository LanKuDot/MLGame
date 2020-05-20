"""
The cross language handler for C++
"""
import os
import os.path
import string
import random

from subprocess import PIPE, Popen

from mlgame.crosslang.exceptions import CompilationError

def compile_script(script_full_path):
    """
    Compile the script to an executable

    The exception will be raised when failed to compile the script.

    @param script_full_path The full path of the target script
    @return The execution command of the executable
    """
    lib_dir = os.path.join(os.path.dirname(__file__), "include")

    dir_path = os.path.dirname(script_full_path)
    main_script_file_path = _preprocess_script(script_full_path, dir_path)
    execute_file_path = os.path.join(dir_path, "ml_play.out")
    if os.path.exists(execute_file_path):
        os.remove(execute_file_path)

    compile_cmd = [
        "g++", main_script_file_path, "-I" + lib_dir, "--std=c++11",
        "-o", execute_file_path
    ]

    with Popen(compile_cmd, bufsize = 1,
        stdout = PIPE, stderr = PIPE, universal_newlines = True) as p:
        outs, errs = p.communicate()

    # Remove the generated script after compilation
    os.remove(main_script_file_path)

    if p.returncode != 0:
        raise CompilationError(os.path.basename(script_full_path), errs)

    return [execute_file_path]

def _preprocess_script(user_script_path, outfile_dir):
    """
    Append the content of user script to "cpp_include/main.cpp" and save to a new file

    @param user_script_path The path of the user script as one of the source
    @param outfile_dir The path of the directory to put the new file
    @return The path of the new file
    """
    basefile_path = os.path.join(os.path.dirname(__file__), "include", "base_main.cpp")
    char_choice = string.ascii_lowercase + string.digits
    outfile_name = ("main_" +
        "".join([random.choice(char_choice) for _ in range(8)]) +
        ".cpp")
    outfile_path = os.path.join(outfile_dir, outfile_name)

    with open(outfile_path, "w") as out_file, \
         open(basefile_path, "r") as in_file:
        # Include the user file
        out_file.write("#include \"{}\"\n".format(os.path.basename(user_script_path)))
        for line in in_file:
            out_file.write(line)

    return outfile_path
