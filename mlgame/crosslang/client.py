"""
The subprocess for running the client script and handling the I/O of it
"""
import json

from subprocess import PIPE, Popen
from threading import Thread, Event
from queue import Queue

from .exceptions import MLClientExecutionError

class Client(Popen):
    """
    The subprocess for executing and communication with non-python client
    """

    def __init__(self, execution_cmd: list):
        """
        Constructor
        """
        super().__init__(execution_cmd, bufsize = 1,
            stdin = PIPE, stdout = PIPE, stderr = PIPE,
            universal_newlines = True)

        # Thread for reading message
        self._command_obj_queue = Queue()
        self._is_program_exited = Event()
        self._read_stdout_thread = Thread(target = self._read_stdout,
            name = "read_stdout")

        self._read_stdout_thread.start()

    def send_to_client(self, header, dict_payload):
        """
        Send the dictionary object to the client
        The object will be converted into a string:
        "<header> <JSON_representation_of_dict_object>".

        @param header The header to be added at the begin of the message
        @param dict_payload A dictionay object
        """
        if not self._is_program_exited.is_set():
            self.stdin.write(header + " " + json.dumps(dict_payload) + "\n")
            self.stdin.flush()

    def recv_from_client(self):
        """
        Receive the command from the subprocess
        It will wait until there has command arrived.
        """
        return self._command_obj_queue.get()

    def _read_stdout(self):
        """
        Read the message from stdout of the client.
        If the message contains "__command__" header, it will be pushed to
        the command object queue. Otherwise, it will be printed out.
        """
        while True:
            message = self.stdout.readline()
            if "__command__" in message:
                # Remove header and the trailing newline
                message = message[12:-1]
                if message == "READY" or message == "RESET":
                    self._command_obj_queue.put(message)
                else:
                    self._command_obj_queue.put(json.loads(message))
            elif len(message):
                print(message, flush = True)
            else:   # zero-length read, program is exited
                break

        self._is_program_exited.set()
        self.wait()

        if self.returncode != 0:
            message = " Get output from stderr:\n" + self._read_stderr()
        else:
            message = ""

        self._command_obj_queue.put(MLClientExecutionError(
            "The user program is exited with returncode {}.{}"
            .format(self.returncode, message)))

    def _read_stderr(self):
        """
        Read the message from stderr of the client.
        """
        message = self.stderr.readlines()
        return "".join(message)
