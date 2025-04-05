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
    """Adapter for database operations with various database engines."""

    def __init__(self, params=None):
        super().__init__(params)
        self._connection = None
        self._cursor = None
        self._operation = None
        self._engine_type = None
        self._connection_string = None
        self._query_result = None
        self._transaction_active = False

    def connect(self, connection_string, engine_type='sqlite'):
        """Connect to a database using the specified engine type and connection string."""
        self._operation = 'connect'
        self._connection_string = connection_string
        self._engine_type = engine_type
        return self

    def query(self, sql, params=None):
        """Execute a SQL query."""
        self._operation = 'query'
        self._params['sql'] = sql
        self._params['query_params'] = params
        return self

    def execute(self, sql, params=None):
        """Execute a SQL statement that doesn't return results."""
        self._operation = 'execute'
        self._params['sql'] = sql
        self._params['query_params'] = params
        return self

    def begin_transaction(self):
        """Begin a transaction."""
        self._operation = 'begin_transaction'
        return self

    def commit(self):
        """Commit the current transaction."""
        self._operation = 'commit'
        return self

    def rollback(self):
        """Rollback the current transaction."""
        self._operation = 'rollback'
        return self

    def table_schema(self, table_name):
        """Get schema information for a table."""
        self._operation = 'table_schema'
        self._params['table_name'] = table_name
        return self

    def insert(self, table_name, data):
        """Insert data into a table."""
        self._operation = 'insert'
        self._params['table_name'] = table_name
        self._params['data'] = data
        return self

    def to_dataframe(self, query=None):
        """Convert query results to pandas DataFrame."""
        self._operation = 'to_dataframe'
        if query:
            self._params['sql'] = query
        return self

    def _execute_self(self, input_data=None):
        try:
            # Connect to database if not already connected
            if self._operation == 'connect' or self._connection is None:
                self._connect_to_database()
                return {"status": "connected", "engine": self._engine_type}

            # Other operations require a connection
            if self._connection is None:
                raise ValueError("Not connected to a database. Call connect() first.")

            # Execute operations
            if self._operation == 'query':
                sql = self._params.get('sql')
                query_params = self._params.get('query_params')

                cursor = self._connection.cursor()
                if query_params:
                    cursor.execute(sql, query_params)
                else:
                    cursor.execute(sql)

                # Get column names
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    # Fetch all results
                    results = cursor.fetchall()
                    # Convert to list of dictionaries
                    self._query_result = [dict(zip(columns, row)) for row in results]
                else:
                    self._query_result = []

                return self._query_result

            elif self._operation == 'execute':
                sql = self._params.get('sql')
                query_params = self._params.get('query_params')

                cursor = self._connection.cursor()
                if query_params:
                    cursor.execute(sql, query_params)
                else:
                    cursor.execute(sql)

                # If not in a transaction, commit automatically
                if not self._transaction_active:
                    self._connection.commit()

                return {"status": "success", "rowcount": cursor.rowcount}

            elif self._operation == 'begin_transaction':
                if not self._transaction_active:
                    self._transaction_active = True
                return {"status": "transaction_started"}

            elif self._operation == 'commit':
                if self._transaction_active:
                    self._connection.commit()
                    self._transaction_active = False
                return {"status": "committed"}

            elif self._operation == 'rollback':
                if self._transaction_active:
                    self._connection.rollback()
                    self._transaction_active = False
                return {"status": "rolled_back"}

            elif self._operation == 'table_schema':
                table_name = self._params.get('table_name')
                sql = f"PRAGMA table_info({table_name})" if self._engine_type == 'sqlite' else f"SELECT * FROM information_schema.columns WHERE table_name = '{table_name}'"

                cursor = self._connection.cursor()
                cursor.execute(sql)
                schema_info = cursor.fetchall()

                if self._engine_type == 'sqlite':
                    columns = ['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk']
                    schema = [dict(zip(columns, row)) for row in schema_info]
                else:
                    # Generic approach for other databases
                    columns = [desc[0] for desc in cursor.description]
                    schema = [dict(zip(columns, row)) for row in schema_info]

                return schema

            elif self._operation == 'insert':
                table_name = self._params.get('table_name')
                data = self._params.get('data')

                if not data:
                    if input_data:
                        data = input_data
                    else:
                        raise ValueError("No data to insert")

                # Handle different input formats
                if isinstance(data, dict):
                    columns = list(data.keys())
                    values = [data[col] for col in columns]
                    placeholders = ','.join(['?'] * len(columns))
                    columns_str = ','.join(columns)

                    sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    cursor = self._connection.cursor()
                    cursor.execute(sql, values)
                elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    # Multiple rows as list of dicts
                    if not data:
                        return {"status": "success", "inserted": 0}

                    columns = list(data[0].keys())
                    columns_str = ','.join(columns)
                    placeholders = ','.join(['?'] * len(columns))

                    sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    cursor = self._connection.cursor()

                    for row in data:
                        values = [row[col] for col in columns]
                        cursor.execute(sql, values)
                else:
                    raise ValueError("Data must be a dictionary or list of dictionaries")

                # If not in a transaction, commit automatically
                if not self._transaction_active:
                    self._connection.commit()

                return {"status": "success", "inserted": cursor.rowcount}

            elif self._operation == 'to_dataframe':
                if 'sql' in self._params:
                    # Execute new query first
                    sql = self._params.get('sql')
                    cursor = self._connection.cursor()
                    cursor.execute(sql)

                    # Get column names
                    columns = [desc[0] for desc in cursor.description]

                    # Fetch all results
                    results = cursor.fetchall()

                    # Convert to DataFrame
                    return pd.DataFrame(results, columns=columns)
                elif self._query_result:
                    # Use existing results
                    return pd.DataFrame(self._query_result)
                else:
                    raise ValueError("No query results to convert to DataFrame")

            # Default handling for direct input
            if input_data is not None:
                if isinstance(input_data, str) and input_data.strip().upper().startswith('SELECT'):
                    # Treat as SQL query
                    self._params['sql'] = input_data
                    return self.query(input_data)._execute_self()

            return self._query_result

        except Exception as e:
            raise RuntimeError(f"Database operation failed: {str(e)}")

    def _connect_to_database(self):
        """Internal method to establish database connection based on engine type."""
        try:
            if self._engine_type == 'sqlite':
                self._connection = sqlite3.connect(self._connection_string)
                # Return dictionary-like rows
                self._connection.row_factory = sqlite3.Row
            elif self._engine_type == 'mysql':
                import mysql.connector
                self._connection = mysql.connector.connect(**json.loads(self._connection_string))
            elif self._engine_type == 'postgresql':
                import psycopg2
                self._connection = psycopg2.connect(self._connection_string)
            elif self._engine_type == 'oracle':
                import cx_Oracle
                self._connection = cx_Oracle.connect(self._connection_string)
            elif self._engine_type == 'sqlserver':
                import pyodbc
                self._connection = pyodbc.connect(self._connection_string)
            else:
                raise ValueError(f"Unsupported database engine: {self._engine_type}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to {self._engine_type} database: {str(e)}")

    def reset(self):
        """Reset adapter state and close any open connections."""
        if self._connection:
            try:
                if self._transaction_active:
                    self._connection.rollback()
                self._connection.close()
            except:
                pass

        self._connection = None
        self._cursor = None
        self._operation = None
        self._query_result = None
        self._transaction_active = False
        self._params = {}
        return self