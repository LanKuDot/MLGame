"""
The interface for coomunicating with the message server
"""

from asgiref.sync import async_to_sync
from channels_redis.core import RedisChannelLayer

class RedisTransition:
	def __init__(self, server_ip, server_port, channel_name):
		"""Constructor

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
