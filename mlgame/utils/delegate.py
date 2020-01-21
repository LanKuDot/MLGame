class FunctionDelegate:
    """
    Simulate the function delegate

    Invoke the registered function by invoking the instance of FunctionDelegate.
    For example:
    ```python
    func_delegate = FunctionDelegate()
    func_delegate.set_function(foo)
    func_delegate()    # Same as foo()
    ```
    """

    def __init__(self):
        self._target_function = None

    def set_function(self, func):
        """
        Set the target function to the function delegate

        @param func A function or a callable object
        """
        if self._target_function is not None:
            raise ValueError("The target function has been already set.")

        if not callable(func):
            raise ValueError("The specified 'func' is not callable.")

        self._target_function = func

    def __call__(self, *args, **kwargs):
        """
        Invoke the registered target function

        This function is invoked by using the instance of FunctionDelegate as a function.
        """
        if self._target_function is None:
            raise RuntimeError("The target function is not specified.")

        return self._target_function(*args, **kwargs)
