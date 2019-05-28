class ExceptionMessage:
	"""The exception message object to be passed to another process
	"""

	def __init__(self, process_name, exc_msg):
		self.process_name = process_name
		self.exc_msg = exc_msg

def trim_callstack(exception_msg: str, target_user_file: str):
	"""
	Shorten the call stack to the starting point of the user script
	"""
	exception_msg_list = exception_msg.splitlines(keepends = True)
	# Store title
	trimmed_msg = exception_msg_list[0]

	# Find the starting point
	i = 0
	for i in range(2, len(exception_msg_list)):
		if target_user_file in exception_msg_list[i]:
			break

	return trimmed_msg + "".join(exception_msg_list[i:])
