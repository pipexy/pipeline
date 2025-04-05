import subprocess
import os
import json
import tempfile
import requests
from typing import Dict, Any, List, Union

# ADAPTERS = {}

class ChainableAdapter:
    """Bazowa klasa dla adapterów, które można łączyć."""

    def __init__(self, name=None, previous=None):
        self.name = name
        self._params = {}
        self._previous = previous
        self._result = None

    def __getattr__(self, name):
        """Umożliwia dostęp do innych adapterów lub metod."""
        if name in ADAPTERS:
            # Zwraca instancję innego adaptera z referencją do aktualnego
            return ADAPTERS[name](previous=self)

        # Tworzy metodę dla danego parametru
        def method(value):
            self._params[name] = value
            return self

        return method

    def execute(self, input_data=None):
        """Wykonuje adapter oraz wszystkie poprzednie w łańcuchu."""
        if self._previous:
            # Wykonaj poprzedni adapter w łańcuchu
            input_data = self._previous.execute(input_data)

        # Wykonaj ten adapter
        return self._execute_self(input_data)

    def _execute_self(self, input_data=None):
        """Implementacja wykonania specyficzna dla konkretnego adaptera."""
        raise NotImplementedError("Subclasses must implement _execute_self()")

    def reset(self):
        """Resetuje parametry adaptera."""
        self._params = {}
        return self