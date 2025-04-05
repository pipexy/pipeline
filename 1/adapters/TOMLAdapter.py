"""
TOMLAdapter.py
"""
import os
import json
import tempfile
from .ChainableAdapter import ChainableAdapter


class TOMLAdapter(ChainableAdapter):
    """Adapter for handling TOML data."""

    def __init__(self, params=None):
        super().__init__(params)
        self._data = None
        self._operation = None
        self._path = None

    def parse_string(self, toml_string):
        """Parse TOML from string."""
        self._operation = 'parse_string'
        self._params['toml_string'] = toml_string
        return self

    def parse_file(self, file_path):
        """Parse TOML from file."""
        self._operation = 'parse_file'
        self._path = file_path
        return self

    def get(self, path):
        """Get value at path."""
        self._operation = 'get'
        self._params['path'] = path
        return self

    def set(self, path, value):
        """Set value at path."""
        self._operation = 'set'
        self._params['path'] = path
        self._params['value'] = value
        return self

    def to_string(self):
        """Convert TOML to string."""
        self._operation = 'to_string'
        return self

    def write_file(self, file_path):
        """Write TOML to file."""
        self._operation = 'write_file'
        self._path = file_path
        return self

    def _execute_self(self, input_data=None):
        try:
            import toml

            # Operations that populate self._data
            if self._operation == 'parse_string':
                toml_str = self._params.get('toml_string')
                self._data = toml.loads(toml_str)
                return self._data

            elif self._operation == 'parse_file':
                if not os.path.exists(self._path):
                    raise FileNotFoundError(f"TOML file not found: {self._path}")
                with open(self._path, 'r', encoding='utf-8') as f:
                    self._data = toml.load(f)
                return self._data

            # Operations that use existing TOML data
            elif self._operation == 'get':
                if self._data is None:
                    if isinstance(input_data, dict):
                        self._data = input_data
                    else:
                        raise ValueError("No TOML data to query")

                path = self._params.get('path')
                if not path:
                    return self._data

                # Split path by dots and traverse the data
                parts = path.split('.')
                result = self._data
                for part in parts:
                    if part in result:
                        result = result[part]
                    else:
                        return None
                return result

            elif self._operation == 'set':
                if self._data is None:
                    if isinstance(input_data, dict):
                        self._data = input_data
                    else:
                        self._data = {}

                path = self._params.get('path')
                value = self._params.get('value')

                # Split path by dots and traverse/create the data structure
                parts = path.split('.')
                target = self._data
                for i, part in enumerate(parts[:-1]):
                    if part not in target:
                        target[part] = {}
                    target = target[part]

                target[parts[-1]] = value
                return self._data

            elif self._operation == 'to_string':
                if self._data is None:
                    if isinstance(input_data, dict):
                        self._data = input_data
                    else:
                        raise ValueError("No TOML data to convert to string")

                return toml.dumps(self._data)

            elif self._operation == 'write_file':
                if self._data is None:
                    if isinstance(input_data, dict):
                        self._data = input_data
                    else:
                        raise ValueError("No TOML data to write")

                with open(self._path, 'w', encoding='utf-8') as f:
                    toml.dump(self._data, f)
                return self._path

            # Default handling for direct input
            if input_data is not None:
                if isinstance(input_data, str):
                    if os.path.exists(input_data):
                        with open(input_data, 'r', encoding='utf-8') as f:
                            self._data = toml.load(f)
                    else:
                        # Try parsing as TOML string
                        try:
                            self._data = toml.loads(input_data)
                        except:
                            raise ValueError("Input is not a valid TOML string or file path")
                elif isinstance(input_data, dict):
                    self._data = input_data

                return self._data

            return self._data

        except ImportError:
            raise RuntimeError("TOML support requires the 'toml' package. Install it with 'pip install toml'")
        except Exception as e:
            raise RuntimeError(f"TOML operation failed: {str(e)}")

    def reset(self):
        """Reset adapter state."""
        self._data = None
        self._operation = None
        self._path = None
        self._params = {}
        return self