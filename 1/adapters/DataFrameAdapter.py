"""
DataFrameAdapter.py
"""
import pandas as pd
import numpy as np
import os
import json
import tempfile
from .ChainableAdapter import ChainableAdapter


class DataFrameAdapter(ChainableAdapter):
    """Adapter for pandas DataFrame operations."""

    def __init__(self, params=None):
        super().__init__(params)
        self._df = None
        self._operation = None

    def load_data(self, data):
        """Load data into DataFrame."""
        self._operation = 'load_data'
        self._params['data'] = data
        return self

    def read_csv(self, file_path, **kwargs):
        """Read data from CSV file."""
        self._operation = 'read_csv'
        self._params['file_path'] = file_path
        self._params['csv_kwargs'] = kwargs
        return self

    def read_excel(self, file_path, **kwargs):
        """Read data from Excel file."""
        self._operation = 'read_excel'
        self._params['file_path'] = file_path
        self._params['excel_kwargs'] = kwargs
        return self

    def read_json(self, file_path_or_string, **kwargs):
        """Read data from JSON file or string."""
        self._operation = 'read_json'
        self._params['source'] = file_path_or_string
        self._params['json_kwargs'] = kwargs
        return self

    def filter(self, condition):
        """Filter DataFrame by condition."""
        self._operation = 'filter'
        self._params['condition'] = condition
        return self

    def select(self, columns):
        """Select columns from DataFrame."""
        self._operation = 'select'
        self._params['columns'] = columns
        return self

    def sort(self, by, ascending=True):
        """Sort DataFrame by column(s)."""
        self._operation = 'sort'
        self._params['by'] = by
        self._params['ascending'] = ascending
        return self

    def groupby(self, columns, agg_dict=None):
        """Group DataFrame by columns."""
        self._operation = 'groupby'
        self._params['columns'] = columns
        self._params['agg_dict'] = agg_dict
        return self

    def apply(self, func):
        """Apply function to DataFrame."""
        self._operation = 'apply'
        self._params['func'] = func
        return self

    def to_csv(self, file_path=None, **kwargs):
        """Write DataFrame to CSV."""
        self._operation = 'to_csv'
        self._params['file_path'] = file_path
        self._params['csv_kwargs'] = kwargs
        return self

    def to_json(self, file_path=None, **kwargs):
        """Write DataFrame to JSON."""
        self._operation = 'to_json'
        self._params['file_path'] = file_path
        self._params['json_kwargs'] = kwargs
        return self

    def to_dict(self, orient='records'):
        """Convert DataFrame to dict."""
        self._operation = 'to_dict'
        self._params['orient'] = orient
        return self

    def describe(self):
        """Get descriptive statistics."""
        self._operation = 'describe'
        return self

    def _execute_self(self, input_data=None):
        try:
            # Operations that populate self._df
            if self._operation == 'load_data':
                data = self._params.get('data')
                self._df = pd.DataFrame(data)
                return self._df

            elif self._operation == 'read_csv':
                file_path = self._params.get('file_path')
                kwargs = self._params.get('csv_kwargs', {})
                self._df = pd.read_csv