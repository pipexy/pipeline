"""
ChainableAdapter.py - Base class for all chainable adapters
"""


class ChainableAdapter:
    def __init__(self, params=None):
        self._params = params or {}
        self._result = None
        self._executed = False
        self._input_data = None

    def __or__(self, other):
        """Handle pipe operator (|) with automatic execution"""
        # Execute this adapter if not already executed
        if not self._executed:
            self._result = self._execute_self(self._input_data)
            self._executed = True

        # Pass result to the next adapter
        if hasattr(other, '__call__'):
            return other(self._result)
        return other

    def __call__(self, input_data=None):
        """Make adapter callable for pipeline execution"""
        # Create new instance with same parameters
        new_instance = self.__class__(self._params.copy() if self._params else {})
        # Store the input data for execution
        new_instance._input_data = input_data
        return new_instance

    def __getattr__(self, name):
        """Handle method chaining without relying on ADAPTERS dictionary"""

        # If attribute is not found, we'll return a method that returns self
        # This helps with method chaining
        def method(*args, **kwargs):
            return self

        return method

    def execute(self):
        """Public method to execute and get results"""
        if not self._executed:
            self._result = self._execute_self(self._input_data)
            self._executed = True
        return self._result

    def _execute_self(self, input_data=None):
        """Default implementation - should be overridden by subclasses"""
        return input_data