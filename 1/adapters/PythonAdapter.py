"""
PythonAdapter.py
"""
import tempfile
import os
import json
import sys
from .ChainableAdapter import ChainableAdapter


class PythonAdapter(ChainableAdapter):
    """Adapter for executing Python code without subprocess."""

    def code(self, python_code):
        """Set Python code to execute."""
        self._params['code'] = python_code
        return self

    def file(self, file_path):
        """Set Python file to execute."""
        self._params['file'] = file_path
        return self

    def _execute_self(self, input_data=None):
        try:
            # Get the code or file
            code = self._params.get('code')
            file_path = self._params.get('file')

            if not code and not file_path:
                raise ValueError("Python adapter requires either 'code' or 'file' parameter")

            # Prepare globals with input data
            global_vars = {'__input__': input_data}

            # Execute the code
            if code:
                # Add input handling
                full_code = f"""
# Input data is available as __input__
input_data = __input__

{code}
                """
                exec(full_code, global_vars)
            elif file_path:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Python file not found: {file_path}")

                with open(file_path, 'r') as f:
                    file_code = f.read()

                # Add input handling to the beginning of the file
                full_code = f"""
# Input data is available as __input__
input_data = __input__

{file_code}
                """
                exec(full_code, global_vars)

            # Check for return value
            if '__return__' in global_vars:
                return global_vars['__return__']

            # If no explicit return, try to find a result variable
            if 'result' in global_vars:
                return global_vars['result']

            return None

        except Exception as e:
            raise RuntimeError(f"Python execution failed: {str(e)}")

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self