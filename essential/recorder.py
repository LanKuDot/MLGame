import pickle
import time

class Recorder:
	"""
	Record the game progress and dump the progress to a file using pickle
	"""

	def __init__(self, saving_status, saving_directory, filename = None):
		"""
		Constructor

		@param saving_status Specify a tuple or a list of game status which
		       indicates that when to dump the game progress to a new file
		@param saving_directory Specify the directory for saving files
		@param filename Specify the name of the file to be generated.
		       If it is not specified, "YYYY-MM-DD_hh-mm-ss.pickle" is used.
		"""
		self.__scene_info_list = []
		self.__saving_status = saving_status
		self.__saving_directory = saving_directory
		self.__create_directory()
		self.__filename = filename

	def __create_directory(self):
		import os
		if not os.path.exists(self.__saving_directory):
			os.mkdir(self.__saving_directory)

	def __save_to_file(self):
		if self.__filename:
			filename = self.__filename
		else:
			filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".pickle"

		filepath = self.__saving_directory + "/" + filename
		with open(filepath, "wb") as f:
			pickle.dump(self.__scene_info_list, f)

	def record_scene_info(self, scene_info):
		"""
		Record the scene info

		The received scene information will be stored in a list.
		When the "status" member of the scene info is the same as one of the
		saving status, the whole list will be dumped to a new file and be cleared.

		@param scene_info The scene information
		"""
		self.__scene_info_list.append(scene_info)
		if scene_info.status in self.__saving_status:
			self.__save_to_file()
			self.__scene_info_list.clear()
