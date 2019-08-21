"""
The interface for communicating with the message server
"""
from asgiref.sync import async_to_sync
from channels_redis.core import RedisChannelLayer

from essential.exception import ExceptionMessage

class RedisTransition:
	def __init__(self, server_ip, server_port, channel_name):
		"""
		Constructor

		@param server_ip Specify the ip of the redis server
		@param server_port Specify the port of the redis server
		@param channel_name Specify the name of the channel in the redis server
		       to be communicated.
		"""
		self._redis_server = RedisChannelLayer(hosts = [(server_ip, int(server_port))])
		self._channel_name = channel_name

	def send(self, message_object):
		async_to_sync(self._redis_server.send)(self._channel_name, message_object)

MessageServer = RedisTransition

class TransitionManager:
	"""
	Receive data sent from the game process and pass it to the remote server
	"""

	def __init__(self, recv_data_func, server_info):
		"""
		Constructor

		@param recv_data_func The function for receiving data
		@param server_info The information of the remote server.
		       A three-element tuple (server_ip, server_port, channel_name).
		"""
		self._recv_data_func = recv_data_func
		self._message_server = MessageServer(*server_info)

	def transition_loop(self):
		"""
		The infinite loop for passing data to the remote server

		If it receives `None`, then quit the transition loop.
		"""
		while True:
			data = self._recv_data_func()

			if not data:
				return
			elif isinstance(data, ExceptionMessage):
				self._send_exception(data)
			else:
				self._message_server.send(data)

	def _send_exception(self, exc_msg: ExceptionMessage):
		"""
		Generate and send the exception message to the remote server
		"""
		self._message_server.send({
			"type": "game_error",
			"data": {
				"message": "Error occurred in \"{}\" process:\n{}" \
					.format(exc_msg.process_name, exc_msg.exc_msg)
			}
		})
