# Bazowa klasa adapterów
"""
base.py
"""



class BaseAdapter:
    """Bazowa klasa dla wszystkich adapterów."""

    def __init__(self, name):
        self.name = name
        self._params = {}

    def __getattr__(self, method_name):
        """Dynamicznie tworzy metody dla różnych parametrów."""

        def method(value):
            self._params[method_name] = value
            return self

        return method

    def execute(self, input_data=None):
        """Wykonuje adapter z ustawionymi parametrami."""
        raise NotImplementedError("Subclasses must implement execute()")

    def reset(self):
        """Resetuje parametry adaptera."""
        self._params = {}
        return self
