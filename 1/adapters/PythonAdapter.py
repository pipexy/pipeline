"""
PythonAdapter.py
"""
import tempfile
import os
import json
import sys
from .ChainableAdapter import ChainableAdapter


class PythonAdapter(ChainableAdapter):
    def __init__(self, params=None):
        super().__init__(params)
        self._code = None

    def execute(self, code_string=None):
        """
        Override execute to either set code or run the pipeline
        """
        if code_string is not None:
            # Store the code string and return self for chaining
            self._code = code_string
            return self
        else:
            # Call parent's execute method (end of chain execution)
            return super().execute()

    def _execute_self(self, input_data=None):
        """Execute the Python code with the input data"""
        if not self._code:
            return input_data

        try:
            # Create a global context with the input data
            global_vars = {'data': input_data}

            # Add imports that might be useful
            import_statements = """
import json
import datetime
import re
"""
            full_code = import_statements + self._code

            # Execute the code in the context
            exec(full_code, global_vars)

            # Look for a result variable or return the last expression
            if 'result' in global_vars:
                return global_vars['result']
            else:
                return input_data

        except Exception as e:
            raise RuntimeError(f"Python execution failed: {str(e)}")