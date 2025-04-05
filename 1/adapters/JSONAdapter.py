"""
JSONAdapter.py
"""
import json
import os
import tempfile
from .ChainableAdapter import ChainableAdapter


class JSONAdapter(ChainableAdapter):
    """Adapter for handling JSON data."""

    def __init__(self, params=None):
        super().__init__(params)
        self._data = None
        self._operation = None
        self._path = None

    def parse_string(self, json_string):
        """Parse JSON from string."""
        self._operation = 'parse_string'
        self._params['json_string'] = json_string
        return self

    def parse_file(self, file_path):
        """Parse JSON from file."""
        self._operation = 'parse_file'
        self._path = file_path
        return self

    def query(self, path):
        """Query JSON with path expression (dot notation or list indices)."""
        self._operation = 'query'
        self._params['path'] = path
        return self

    def create(self, data):
        """Create new JSON object."""
        self._operation = 'create'
        self._params['data'] = data
        return self

    def to_string(self, pretty=True):
        """Convert JSON to string."""
        self._operation = 'to_string'
        self._params['pretty'] = pretty
        return self

    def write_file(self, file_path):
        """Write JSON to file."""
        self._operation = 'write_file'
        self._path = file_path
        return self

    def transform(self, transform_func):
        """Apply transformation function to JSON."""
        self._operation = 'transform'
        self._params['transform_func'] = transform_func
        return self

    def _execute_self(self, input_data=None):
        try:
            # Operations that populate self._data
            if self._operation == 'parse_string':
                json_str = self._params.get('json_string')
                self._data = json.loads(json_str)
                return self._data

            elif self._operation == 'parse_file':
                if not os.path.exists(self._path):
                    raise FileNotFoundError(f"JSON file not found: {self._path}")
                with open(self._path, 'r') as f:
                    self._data = json.load(f)
                return self._data

            elif self._operation == 'create':
                self._data = self._params.get('data')
                return self._data

            # Operations that use existing JSON data
            elif self._operation == 'query':
                if self._data is None:
                    if input_data is not None:
                        self._data = input_data
                    else:
                        raise ValueError("No JSON data to query")

                path = self._params.get('path')
                if not path:
                    return self._data

                # Handle path expressions (e.g., "users.0.name")
                result = self._data
                for key in path.split('.'):
                    if key.isdigit():
                        key = int(key)
                    result = result[key]
                return result

            elif self._operation == 'to_string':
                if self._data is None:
                    if input_data is not None:
                        self._data = input_data
                    else:
                        raise ValueError("No JSON data to convert")

                indent = 2 if self._params.get('pretty', True) else None
                return json.dumps(self._data, indent=indent)

            elif self._operation == 'write_file':
                if self._data is None:
                    if input_data is not None:
                        self._data = input_data
                    else:
                        raise ValueError("No JSON data to write")

                indent = 2 if self._params.get('pretty', True) else None
                with open(self._path, 'w') as f:
                    json.dump(self._data, f, indent=indent)
                return self._path

            elif self._operation == 'transform':
                if self._data is None:
                    if input_data is not None:
                        self._data = input_data
                    else:
                        raise ValueError("No JSON data to transform")

                transform_func = self._params.get('transform_func')
                if not callable(transform_func):
                    raise ValueError("Transform function is not callable")

                self._data = transform_func(self._data)
                return self._data

            # Default handling for direct input
            if input_data is not None:
                if isinstance(input_data, str):
                    if os.path.exists(input_data):
                        with open(input_data, 'r') as f:
                            self._data = json.load(f)
                    else:
                        self._data = json.loads(input_data)
                else:
                    self._data = input_data

                return self._data

            return self._data

        except Exception as e:
            raise RuntimeError(f"JSON operation failed: {str(e)}")

    def reset(self):
        """Reset adapter state."""
        self._data = None
        self._operation = None
        self._path = None
        self._params = {}
        return self