import pickle
import time
import os

class Recorder:
    """
    Record the game progress and dump the progress to a file using pickle
    """

    def __init__(self, saving_directory):
        """
        Constructor

        @param saving_directory Specify the directory for saving files
        """
        self.__scene_info_list = []
        self.__saving_directory = saving_directory
        self.__create_directory()

    def __create_directory(self):
        if not os.path.exists(self.__saving_directory):
            os.mkdir(self.__saving_directory)

    def flush_to_file(self, filename_prefix = ""):
        """
        Flush the stored objects to the file

        @param filename_prefix Specify the prefix of the filename to be generated.
               The filename will be "<prefix>_YYYY-MM-DD_hh-mm-ss.pickle".
        """
        if not isinstance(filename_prefix, str):
            raise TypeError("'filename_prefix' should be the type of 'str'")

        filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".pickle"

        if filename_prefix != "":
            filename = filename_prefix + "_" + filename

        filepath = os.path.join(self.__saving_directory, filename)
        with open(filepath, "wb") as f:
            pickle.dump(self.__scene_info_list, f)

        self.__scene_info_list.clear()

    def record_scene_info(self, scene_info):
        """
        Record the scene info

        The received scene information will be stored in a list.

        @param scene_info The scene information
        """
        self.__scene_info_list.append(scene_info)

class RecorderHelper:
    """
    A helper class that wrap the recording steps into one function call
    """

    def __init__(self, log_dir, saving_status: dict, filename_prefix = ""):
        """
        Constructor

        @param log_dir The path of directory for saving log files
        @param saving_status A dictionary for indicating when to flush the saved progress
           to a file. The key is the name of the member of the progress object,
           the value is a list of possible values of that member.
        @param filename_prefix The prefix of the filename
        """
        self._recorder = Recorder(log_dir)
        self._saving_status = saving_status
        self._filename_prefix = filename_prefix

    def record_handler(self, progress_object: dict):
        """
        A handler for passing the `progress_object` to the created recorder.
        If the member of the `progress_object` matches the `saving_status` specified
        at the constructor, it will make the recorder flush the saved progress to a file.

        @param progress_object A dictionary object to be saved by the recorder
        """
        self._recorder.record_scene_info(progress_object)

        for member, values in self._saving_status.items():
            target_value = progress_object.get(member, None)

            if target_value and target_value in values:
                self._recorder.flush_to_file(self._filename_prefix)
                break
