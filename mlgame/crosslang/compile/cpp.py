"""
The cross language handler for C++
"""
import os.path

from subprocess import PIPE, Popen

def compile_script(script_full_path):
    """
    Compile the script to an executable

    The exception will be raised when failed to compile the script.

    @param script_full_path The full path of the target script
    @return The execution command of the executable
    """
    dir_path = os.path.dirname(script_full_path)
    output_file_path = os.path.join(dir_path, "ml_play.out")
    compile_cmd = ["g++", script_full_path, "-o", output_file_path]

    with Popen(compile_cmd, bufsize = 1,
        stdout = PIPE, stderr = PIPE, universal_newlines = True) as p:
        outs, errs = p.communicate()

    if p.returncode != 0:
        raise RuntimeError("Failed to compile the script\n" + errs)

    return output_file_path
