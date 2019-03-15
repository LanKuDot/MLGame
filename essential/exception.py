class ExceptionMessage:
	"""The exception message object to be passed to another process
	"""

	def __init__(self, process_name, exc_msg):
		self.process_name = process_name
		self.exc_msg = exc_msg
