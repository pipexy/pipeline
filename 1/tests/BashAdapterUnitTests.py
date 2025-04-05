# tests/test_bash_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
import subprocess

# Import the adapter to test
sys.path.append('..')
from adapters.BashAdapter import BashAdapter


class BashAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of BashAdapter"""
        adapter = BashAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    @patch('subprocess.run')
    def test_execute_command(self, mock_run):
        """Test executing a simple bash command"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b"test output\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = BashAdapter({})
        adapter.command("echo 'test'")
        result = adapter.execute()

        # Verify the command was executed
        mock_run.assert_called_once()
        self.assertEqual(result, "test output")

    @patch('subprocess.run')
    def test_error_handling(self, mock_run):
        """Test handling of command errors"""
        # Mock a failed subprocess.run
        process_mock = MagicMock()
        process_mock.stderr = b"command not found: invalid_command\n"
        process_mock.returncode = 127
        mock_run.return_value = process_mock

        adapter = BashAdapter({})
        adapter.command("invalid_command")

        # Test if the adapter properly handles errors
        with self.assertRaises(Exception):
            adapter.execute()

    def test_environment_variables(self):
        """Test setting environment variables"""
        adapter = BashAdapter({})
        adapter.command("echo $TEST_VAR")
        adapter.env({"TEST_VAR": "test_value"})

        with patch('subprocess.run') as mock_run:
            process_mock = MagicMock()
            process_mock.stdout = b"test_value\n"
            process_mock.returncode = 0
            mock_run.return_value = process_mock

            result = adapter.execute()

            # Verify env vars were passed correctly
            called_env = mock_run.call_args[1]['env']
            self.assertEqual(called_env.get("TEST_VAR"), "test_value")
            self.assertEqual(result, "test_value")

    def test_working_directory(self):
        """Test setting working directory"""
        adapter = BashAdapter({})
        adapter.command("pwd")
        adapter.cwd(self.test_dir)

        with patch('subprocess.run') as mock_run:
            process_mock = MagicMock()
            process_mock.stdout = self.test_dir.encode() + b"\n"
            process_mock.returncode = 0
            mock_run.return_value = process_mock

            result = adapter.execute()

            # Verify working directory was set correctly
            mock_run.assert_called_once()
            self.assertEqual(mock_run.call_args[1]['cwd'], self.test_dir)
            self.assertEqual(result, self.test_dir)


if __name__ == "__main__":
    unittest.main()