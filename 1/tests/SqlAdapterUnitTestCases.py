# tests/test_sql_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import pandas as pd

# Import the adapter to test
sys.path.append('..')
from adapters.SqlAdapter import SqlAdapter


class SqlAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test database configuration
        self.db_config = {
            "connection_string": "sqlite:///:memory:",
            "dialect": "sqlite"
        }

    def test_initialization(self):
        """Test basic initialization of SqlAdapter"""
        adapter = SqlAdapter(self.db_config)
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, self.db_config)

    @patch('sqlalchemy.create_engine')
    @patch('pandas.read_sql')
    def test_execute_query(self, mock_read_sql, mock_create_engine):
        """Test executing a SQL query"""
        # Mock the engine and query result
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Create a sample DataFrame as return value
        df = pd.DataFrame({'id': [1, 2], 'name': ['John', 'Jane']})
        mock_read_sql.return_value = df

        adapter = SqlAdapter(self.db_config)
        adapter.query("SELECT * FROM users")
        result = adapter.execute()

        # Verify the query was executed
        mock_create_engine.assert_called_once_with(self.db_config["connection_string"])
        mock_read_sql.assert_called_once_with("SELECT * FROM users", mock_engine)

        # Result should be the DataFrame
        pd.testing.assert_frame_equal(result, df)

    @patch('sqlalchemy.create_engine')
    def test_execute_statement(self, mock_create_engine):
        """Test executing a SQL statement (non-query)"""
        # Mock the engine and connection
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_connection = MagicMock()
        mock_engine.connect.return_value = mock_connection

        mock_context = MagicMock()
        mock_connection.__enter__.return_value = mock_context

        # Mock transaction execution
        mock_execute = MagicMock()
        mock_context.execute = mock_execute
        mock_execute.return_value.rowcount = 2  # Simulate 2 rows affected

        adapter = SqlAdapter(self.db_config)
        adapter.statement("INSERT INTO users (name) VALUES ('John'), ('Jane')")
        result = adapter.execute()

        # Verify the statement was executed
        mock_create_engine.assert_called_once_with(self.db_config["connection_string"])
        mock_context.execute.assert_called_once_with(
            "INSERT INTO users (name) VALUES ('John'), ('Jane')"
        )

        # Result should be the number of affected rows
        self.assertEqual(result, 2)

    @patch('sqlalchemy.create_engine')
    def test_transaction_handling(self, mock_create_engine):
        """Test handling transactions"""
        # Mock the engine and connection
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_connection = MagicMock()
        mock_engine.connect.return_value = mock_connection

        mock_context = MagicMock()
        mock_connection.__enter__.return_value = mock_context

        # Set up multiple statements
        statements = [
            "INSERT INTO users (name) VALUES ('John')",
            "UPDATE users SET status = 'active' WHERE name = 'John'"
        ]

        # Mock execution results
        mock_context.execute.side_effect = [
            MagicMock(rowcount=1),
            MagicMock(rowcount=1)
        ]

        adapter = SqlAdapter(self.db_config)
        adapter.transaction(statements)
        result = adapter.execute()

        # Verify both statements were executed in transaction
        self.assertEqual(mock_context.execute.call_count, 2)
        mock_context.execute.assert_any_call(statements[0])
        mock_context.execute.assert_any_call(statements[1])

        # Result should be a list of affected row counts
        self.assertEqual(result, [1, 1])

    @patch('sqlalchemy.create_engine')
    def test_error_handling(self, mock_create_engine):
        """Test handling SQL errors"""
        # Mock the engine to raise an exception
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_connection = MagicMock()
        mock_engine.connect.return_value = mock_connection

        mock_context = MagicMock()
        mock_connection.__enter__.return_value = mock_context

        # Simulate a SQL error
        mock_context.execute.side_effect = Exception("SQL syntax error")

        adapter = SqlAdapter(self.db_config)
        adapter.statement("INSERT INTO nonexistent_table VALUES (1)")

        # Should propagate the error
        with self.assertRaises(Exception):
            adapter.execute()

    @patch('sqlalchemy.create_engine')
    @patch('pandas.read_sql')
    def test_parameterized_query(self, mock_read_sql, mock_create_engine):
        """Test executing a parameterized query"""
        # Mock the engine and query result
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Create a sample DataFrame as return value
        df = pd.DataFrame({'id': [1], 'name': ['John']})
        mock_read_sql.return_value = df

        adapter = SqlAdapter(self.db_config)
        adapter.query("SELECT * FROM users WHERE id = :user_id")
        adapter.params({"user_id": 1})
        result = adapter.execute()

        # Verify the parameterized query was executed
        mock_create_engine.assert_called_once_with(self.db_config["connection_string"])
        mock_read_sql.assert_called_once_with(
            "SELECT * FROM users WHERE id = :user_id",
            mock_engine,
            params={"user_id": 1}
        )

        # Result should be the DataFrame
        pd.testing.assert_frame_equal(result, df)


if __name__ == "__main__":
    unittest.main()