# Adapter do baz danych
"""
database_adapter.py
"""
import os
import json
import ChainableAdapter



class DatabaseAdapter(ChainableAdapter):
    """Adapter do operacji bazodanowych."""

    def _execute_self(self, input_data=None):
        db_type = self._params.get('type', 'sqlite')
        connection_string = self._params.get('connection')
        query = self._params.get('query')

        if not query:
            raise ValueError("Database adapter requires 'query' method")

        if db_type == 'sqlite':
            import sqlite3

            # Obsługa SQLite
            conn = sqlite3.connect(connection_string or ':memory:')
            cursor = conn.cursor()

            # Wykonanie zapytania
            if isinstance(input_data, dict):
                cursor.execute(query, input_data)
            elif isinstance(input_data, list) and all(isinstance(item, dict) for item in input_data):
                cursor.executemany(query, input_data)
            else:
                cursor.execute(query)

            # Pobranie wyników
            if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                conn.commit()
                result = {'affected_rows': cursor.rowcount}

            conn.close()
            return result

        elif db_type == 'mysql':
            try:
                import mysql.connector

                # Obsługa MySQL
                conn = mysql.connector.connect(**json.loads(connection_string))
                cursor = conn.cursor(dictionary=True)

                # Wykonanie zapytania
                if isinstance(input_data, dict):
                    cursor.execute(query, input_data)
                elif isinstance(input_data, list) and all(isinstance(item, dict) for item in input_data):
                    cursor.executemany(query, input_data)
                else:
                    cursor.execute(query)

                # Pobranie wyników
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = {'affected_rows': cursor.rowcount}

                cursor.close()
                conn.close()
                return result

            except ImportError:
                raise ImportError("mysql-connector-python is required for MySQL connections")

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

