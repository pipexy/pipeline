"""
SQLAdapter.py
"""
import sqlite3
import tempfile
import os
import json
import pandas as pd
from .ChainableAdapter import ChainableAdapter


class SQLAdapter(ChainableAdapter):
    """Adapter for executing SQL queries."""

    def __init__(self, params=None):
        super().__init__(params)
        self._conn = None
        self._db_path = ':memory:'  # Default to in-memory database

    def connect(self, db_path=':memory:'):
        """Connect to a database."""
        self._db_path = db_path
        return self

    def query(self, sql_query):
        """Execute a SQL query."""
        self._params['query'] = sql_query
        return self

    def execute_script(self, sql_script):
        """Execute a SQL script."""
        self._params['script'] = sql_script
        return self

    def import_data(self, table_name, data):
        """Import data into a table."""
        self._params['table_name'] = table_name
        self._params['import_data'] = data
        return self

    def _execute_self(self, input_data=None):
        temp_db = None

        try:
            # Create or connect to database
            if self._db_path == ':memory:' and 'db_file' in self._params:
                self._db_path = self._params['db_file']

            # If input is a file path and we're using in-memory DB, use that file instead
            if isinstance(input_data, str) and os.path.exists(input_data) and self._db_path == ':memory:':
                self._db_path = input_data

            # Connect to database
            self._conn = sqlite3.connect(self._db_path)

            # Import data if specified
            if 'import_data' in self._params and 'table_name' in self._params:
                data = self._params['import_data']
                table_name = self._params['table_name']

                if isinstance(data, pd.DataFrame):
                    data.to_sql(table_name, self._conn, if_exists='replace', index=False)
                elif isinstance(data, (list, dict)):
                    df = pd.DataFrame(data)
                    df.to_sql(table_name, self._conn, if_exists='replace', index=False)

            # Execute script if provided
            if 'script' in self._params:
                self._conn.executescript(self._params['script'])
                self._conn.commit()
                return True

            # Execute query if provided
            if 'query' in self._params:
                query = self._params['query']
                cursor = self._conn.cursor()
                cursor.execute(query)

                # Check if this is a SELECT query
                if query.strip().upper().startswith('SELECT'):
                    # Get column names
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()

                    # Convert to DataFrame if pandas is available
                    return pd.DataFrame(results, columns=columns)
                else:
                    self._conn.commit()
                    return cursor.rowcount  # Return number of affected rows

            # If input_data is a query string, execute it
            if isinstance(input_data, str) and (
                input_data.strip().upper().startswith('SELECT') or
                input_data.strip().upper().startswith('INSERT') or
                input_data.strip().upper().startswith('UPDATE') or
                input_data.strip().upper().startswith('DELETE')
            ):
                cursor = self._conn.cursor()
                cursor.execute(input_data)
                self._conn.commit()

                if input_data.strip().upper().startswith('SELECT'):
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()
                    return pd.DataFrame(results, columns=columns)
                else:
                    return cursor.rowcount

            # Default: return the connection object
            return self._conn

        except Exception as e:
            raise RuntimeError(f"SQL operation failed: {str(e)}")

        finally:
            # Close connection if it exists and is not in-memory
            if self._conn and self._db_path != ':memory:':
                self._conn.close()

    def reset(self):
        """Reset adapter state."""
        if self._conn:
            self._conn.close()
        self._conn = None
        self._db_path = ':memory:'
        self._params = {}
        return self