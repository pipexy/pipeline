#!/usr/bin/env python3
# PythonAdapter.py

from .BaseAdapter import BaseAdapter

class PythonAdapter(BaseAdapter):
    """Adapter wykonujący kod Python."""

    def execute(self, input_data=None):
        code = self._params.get('code')
        func = self._params.get('function')

        if not code and not func:
            raise ValueError("Python adapter requires 'code' or 'function' method")

        # Jeśli podano funkcję
        if func:
            if not callable(func):
                raise ValueError("'function' parameter must be callable")
            return func(input_data, **self._params.get('args', {}))

        # Jeśli podano kod
        if code:
            # Utwórz środowisko wykonawcze
            globals_dict = {
                'input_data': input_data,
                'params': self._params,
                'result': None
            }

            # Wykonaj kod
            exec(code, globals_dict)

            # Zwróć wynik
            return globals_dict.get('result')

        return None
