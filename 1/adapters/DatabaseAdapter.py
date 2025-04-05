"""
DatabaseAdapter.py
"""
import sqlite3
import pandas as pd
import os
import json
import tempfile
from .ChainableAdapter import ChainableAdapter


class DatabaseAdapter(ChainableAdapter):
    def __init__(self, params=None):
        super().__init__(params)
        self._connection = None
        self._table = None
        self._operation = None
        self._query = None
        self._data = None

    def connect(self, database_path):
        """Connect to SQLite database"""
        self._params['database_path'] = database_path
        return self

    def insert(self, table_name):
        """Set up an insert operation"""
        self._operation = 'INSERT'
        self._table = table_name
        # Data will be provided from the pipeline's input_data
        return self

    def _execute_self(self, input_data=None):
        """Execute the database operation"""
        import sqlite3

        try:
            # Initialize result with a default value
            result = {'status': 'No operation performed'}

            # Use input_data from the pipeline as our data source
            self._data = input_data

            # Connect to database
            conn = sqlite3.connect(self._params.get('database_path', ':memory:'))
            cursor = conn.cursor()

            if self._operation == 'INSERT' and self._data:
                # Create table if it doesn't exist
                if isinstance(self._data, list) and len(self._data) > 0:
                    sample = self._data[0]
                    columns = list(sample.keys())
                    columns_sql = ', '.join(f'"{col}" TEXT' for col in columns)
                    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{self._table}" ({columns_sql})')

                    # Insert data
                    inserted = 0
                    for item in self._data:
                        placeholders = ', '.join(['?'] * len(item))
                        columns_str = ', '.join([f'"{col}"' for col in item.keys()])
                        values = list(item.values())

                        cursor.execute(
                            f'INSERT INTO "{self._table}" ({columns_str}) VALUES ({placeholders})',
                            values
                        )
                        inserted += 1

                    conn.commit()
                    result = {'inserted': inserted}
                else:
                    result = {'inserted': 0}

            conn.close()
            return result

        except Exception as e:
            raise RuntimeError(f"Database operation failed: {str(e)}")