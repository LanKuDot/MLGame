"""
The exceptions for the crosslang module
"""

class CompilationError(Exception):
    """
    Exception raised when failed to compile the user script
    """
    def __init__(self, file, reason):
        self.file = file
        self.reason = reason

    def __str__(self):
        return "Failed to compile '{}':\n{}".format(self.file, self.reason)

class MLClientExecutionError(Exception):
    """
    Exception raised when an error occurred while running non-python ml script
    """
    def __init__(self, message):
        """
        Constructor
        """
        self.message = message

    def __str__(self):
        return self.message
