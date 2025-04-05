"""
CSVAdapter.py
"""
import pandas as pd
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class CSVAdapter(ChainableAdapter):
    """Adapter for reading, manipulating, and writing CSV data."""

    def __init__(self, params=None):
        super().__init__(params)
        self._dataframe = None
        self._operation = None
        self._file_path = None

    def read_file(self, file_path):
        """Read CSV from a file."""
        self._operation = 'read_file'
        self._file_path = file_path
        return self

    def write_file(self, file_path):
        """Write CSV to a file."""
        self._operation = 'write_file'
        self._file_path = file_path
        return self

    def filter(self, condition):
        """Filter rows by condition."""
        self._operation = 'filter'
        self._params['condition'] = condition
        return self

    def sort(self, column, ascending=True):
        """Sort by column."""
        self._operation = 'sort'
        self._params['column'] = column
        self._params['ascending'] = ascending
        return self

    def _execute_self(self, input_data=None):
        try:
            # Handle different operations
            if self._operation == 'read_file':
                if not os.path.exists(self._file_path):
                    raise FileNotFoundError(f"CSV file not found: {self._file_path}")
                self._dataframe = pd.read_csv(self._file_path)
                return self._dataframe

            elif self._operation == 'write_file':
                if self._dataframe is not None:
                    self._dataframe.to_csv(self._file_path, index=False)
                elif isinstance(input_data, pd.DataFrame):
                    input_data.to_csv(self._file_path, index=False)
                else:
                    raise ValueError("No DataFrame available to write")
                return self._file_path

            elif self._operation == 'filter':
                if self._dataframe is None:
                    if isinstance(input_data, pd.DataFrame):
                        self._dataframe = input_data
                    else:
                        raise ValueError("No DataFrame to filter")

                condition = self._params.get('condition')
                if callable(condition):
                    self._dataframe = self._dataframe[self._dataframe.apply(condition, axis=1)]
                else:
                    self._dataframe = eval(f"self._dataframe[{condition}]")
                return self._dataframe

            elif self._operation == 'sort':
                if self._dataframe is None:
                    if isinstance(input_data, pd.DataFrame):
                        self._dataframe = input_data
                    else:
                        raise ValueError("No DataFrame to sort")

                column = self._params.get('column')
                ascending = self._params.get('ascending', True)
                self._dataframe = self._dataframe.sort_values(column, ascending=ascending)
                return self._dataframe

            # If no operation specified or it's a direct execution
            if input_data is not None:
                if isinstance(input_data, pd.DataFrame):
                    return input_data
                elif isinstance(input_data, str) and os.path.exists(input_data):
                    return pd.read_csv(input_data)
                elif isinstance(input_data, (list, dict)):
                    return pd.DataFrame(input_data)

            return self._dataframe if self._dataframe is not None else pd.DataFrame()

        except Exception as e:
            raise RuntimeError(f"CSV operation failed: {str(e)}")

    def reset(self):
        """Reset adapter state."""
        self._dataframe = None
        self._operation = None
        self._file_path = None
        self._params = {}
        return self