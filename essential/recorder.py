import pickle, time
from .game_base import BasicSceneInfo

class Recorder:
	def __init__(self, saving_directory, filename = None):
		self.__scene_info_list = []
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

	def record_scene_info(self, scene_info: BasicSceneInfo):
		self.__scene_info_list.append(scene_info)
		if scene_info.status == BasicSceneInfo.STATUS_GAME_OVER or \
		   scene_info.status == BasicSceneInfo.STATUS_GAME_PASS:
			self.__save_to_file()
			self.__scene_info_list.clear()
