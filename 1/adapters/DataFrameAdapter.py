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
        # Operations that populate self._df
        if self._operation == 'load_data':
            data = self._params.get('data')
            self._df = pd.DataFrame(data)
            return self._df

        elif self._operation == 'read_csv':
            file_path = self._params.get('file_path')
            kwargs = self._params.get('csv_kwargs', {})
            try:
                self._df = pd.read_csv(file_path, **kwargs)
            except Exception as e:
                raise RuntimeError(f"Error reading CSV file: {str(e)}")

        elif self._operation == 'read_excel':
            file_path = self._params.get('file_path')
            kwargs = self._params.get('excel_kwargs', {})
            try:
                self._df = pd.read_excel(file_path, **kwargs)
            except Exception as e:
                raise RuntimeError(f"Error reading Excel file: {str(e)}")

        elif self._operation == 'read_json':
            source = self._params.get('source')
            kwargs = self._params.get('json_kwargs', {})
            try:
                if os.path.exists(source):
                    self._df = pd.read_json(source, **kwargs)
                else:
                    self._df = pd.read_json(source, **kwargs)
            except Exception as e:
                raise RuntimeError(f"Error reading JSON: {str(e)}")

        # Use input_data if available and no operation is specified
        if self._df is None and input_data is not None:
            if isinstance(input_data, pd.DataFrame):
                self._df = input_data
            else:
                try:
                    self._df = pd.DataFrame(input_data)
                except Exception as e:
                    raise RuntimeError(f"Error converting input data to DataFrame: {str(e)}")

        # Operations that transform existing DataFrame
        if self._df is not None:
            if self._operation == 'filter':
                condition = self._params.get('condition')
                if callable(condition):
                    self._df = self._df[condition(self._df)]
                else:
                    self._df = self._df.query(condition)

            elif self._operation == 'select':
                columns = self._params.get('columns')
                self._df = self._df[columns]

            elif self._operation == 'sort':
                by = self._params.get('by')
                ascending = self._params.get('ascending', True)
                self._df = self._df.sort_values(by=by, ascending=ascending)

            elif self._operation == 'groupby':
                columns = self._params.get('columns')
                agg_dict = self._params.get('agg_dict')
                if agg_dict:
                    self._df = self._df.groupby(columns).agg(agg_dict).reset_index()
                else:
                    self._df = self._df.groupby(columns).sum().reset_index()

            elif self._operation == 'apply':
                func = self._params.get('func')
                self._df = self._df.apply(func)

            elif self._operation == 'to_csv':
                file_path = self._params.get('file_path')
                kwargs = self._params.get('csv_kwargs', {})
                if file_path:
                    self._df.to_csv(file_path, **kwargs)
                    return {"file_path": file_path, "rows": len(self._df)}
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as f:
                        self._df.to_csv(f.name, **kwargs)
                        return {"file_path": f.name, "rows": len(self._df)}

            elif self._operation == 'to_json':
                file_path = self._params.get('file_path')
                kwargs = self._params.get('json_kwargs', {})
                if file_path:
                    self._df.to_json(file_path, **kwargs)
                    return {"file_path": file_path, "rows": len(self._df)}
                else:
                    return self._df.to_json(**kwargs)

            elif self._operation == 'to_dict':
                orient = self._params.get('orient', 'records')
                return self._df.to_dict(orient=orient)

            elif self._operation == 'describe':
                return self._df.describe().to_dict()

        return self._df