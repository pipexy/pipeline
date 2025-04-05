#!/usr/bin/env python3
# YAMLAdapter.py

import yaml
import os
import json
from .ChainableAdapter import ChainableAdapter


class YAMLAdapter(ChainableAdapter):
    """Adapter for handling YAML data."""

    def __init__(self, config=None):
        super().__init__(config)
        self._data = None
        self._operation = None
        self._path = None

    def parse_string(self, yaml_string):
        """Parse YAML from string."""
        self._operation = 'parse_string'
        self._params['yaml_string'] = yaml_string
        return self

    def parse_file(self, file_path):
        """Parse YAML from file."""
        self._operation = 'parse_file'
        self._path = file_path
        return self

    def query_path(self, path_expr):
        """Query specific path from YAML."""
        self._operation = 'query_path'
        self._params['path_expr'] = path_expr
        return self

    def create_object(self, data):
        """Create a new YAML object."""
        self._operation = 'create_object'
        self._params['data'] = data
        return self

    def to_string(self):
        """Convert data to YAML string."""
        self._operation = 'to_string'
        return self

    def write_file(self, file_path):
        """Write YAML to file."""
        self._operation = 'write_file'
        self._path = file_path
        return self

    def _execute_self(self, input_data=None):
        try:
            # Operations that populate self._data
            if self._operation == 'parse_string':
                yaml_str = self._params.get('yaml_string')
                self._data = yaml.safe_load(yaml_str)
                return self._data

            elif self._operation == 'parse_file':
                if not os.path.exists(self._path):
                    raise FileNotFoundError(f"YAML file not found: {self._path}")
                with open(self._path, 'r') as f:
                    self._data = yaml.safe_load(f)
                return self._data

            elif self._operation == 'create_object':
                self._data = self._params.get('data')
                return self._data

            # Operations that use existing data
            elif self._operation == 'query_path':
                if self._data is None:
                    if input_data is not None:
                        self._data = input_data
                    else:
                        raise ValueError("No YAML data to query")

                path_expr = self._params.get('path_expr')
                result = self._data
                for key in path_expr.replace('[', '.').replace(']', '').split('.'):
                    if key == '':
                        continue
                    if key.isdigit():
                        result = result[int(key)]
                    else:
                        result = result[key]
                return result

            elif self._operation == 'to_string':
                if self._data is None:
                    if input_data is not None:
                        self._data = input_data
                    else:
                        raise ValueError("No YAML data to convert")

                return yaml.dump(self._data, default_flow_style=False)

            elif self._operation == 'write_file':
                if self._data is None:
                    if input_data is not None:
                        self._data = input_data
                    else:
                        raise ValueError("No YAML data to write")

                with open(self._path, 'w') as f:
                    yaml.dump(self._data, f, default_flow_style=False)
                return self._path

            # Default behavior
            if input_data is not None:
                self._data = input_data

            return self._data

        except Exception as e:
            raise RuntimeError(f"YAML operation failed: {str(e)}")

    def reset(self):
        """Reset adapter state."""
        self._data = None
        self._operation = None
        self._path = None
        self._params = {}
        return self