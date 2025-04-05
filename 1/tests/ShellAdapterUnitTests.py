# tests/test_shell_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile

# Import the adapter to test
sys.path.append('..')
from adapters.ShellAdapter import ShellAdapter


class ShellAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of ShellAdapter"""
        adapter = ShellAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    @patch('subprocess.run')
    def test_command_execution(self, mock_run):
        """Test executing a shell command"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b"Hello, Shell World\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = ShellAdapter({})
        adapter.command("echo 'Hello, Shell World'")
        result = adapter.execute()

        # Verify the command was executed
        mock_run.assert_called_once()
        self.assertEqual(result, "Hello, Shell World")

    @patch('subprocess.run')
    def test_command_with_arguments(self, mock_run):
        """Test command with arguments"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b"arg1 arg2\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = ShellAdapter({})
        adapter.command("echo")
        adapter.args(["arg1", "arg2"])
        result = adapter.execute()

        # Verify the command and args were executed
        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        self.assertEqual(cmd_args[0], "echo")
        self.assertEqual(cmd_args[1], "arg1")
        self.assertEqual(cmd_args[2], "arg2")
        self.assertEqual(result, "arg1 arg2")

    @patch('subprocess.run')
    def test_environment_variables(self, mock_run):
        """Test setting environment variables"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b"test_value\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = ShellAdapter({})
        adapter.command("echo $TEST_VAR")
        adapter.env({"TEST_VAR": "test_value"})
        result = adapter.execute()

        # Verify env vars were passed correctly
        mock_run.assert_called_once()
        called_env = mock_run.call_args[1]['env']
        self.assertTrue("TEST_VAR" in called_env)
        self.assertEqual(called_env["TEST_VAR"], "test_value")
        self.assertEqual(result, "test_value")

    @patch('subprocess.run')
    def test_working_directory(self, mock_run):
        """Test setting working directory"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b"Current directory\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = ShellAdapter({})
        adapter.command("pwd")
        adapter.cwd(self.test_dir)
        result = adapter.execute()

        # Verify working directory was set
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args[1]['cwd'], self.test_dir)

    @patch('subprocess.run')
    def test_error_handling(self, mock_run):
        """Test handling command errors"""
        # Mock a failed subprocess.run
        process_mock = MagicMock()
        process_mock.stderr = b"command not found: invalid_command\n"
        process_mock.returncode = 127  # Command not found
        mock_run.return_value = process_mock

        adapter = ShellAdapter({})
        adapter.command("invalid_command")

        # Test if the adapter properly handles errors
        with self.assertRaises(Exception):
            adapter.execute()

    @patch('subprocess.run')
    def test_ignore_errors(self, mock_run):
        """Test ignoring command errors"""
        # Mock a failed subprocess.run
        process_mock = MagicMock()
        process_mock.stderr = b"command not found: invalid_command\n"
        process_mock.stdout = b""
        process_mock.returncode = 127  # Command not found
        mock_run.return_value = process_mock

        adapter = ShellAdapter({"ignore_errors": True})
        adapter.command("invalid_command")
        result = adapter.execute()

        # Should not raise an exception
        self.assertEqual(result, "")

    @patch('subprocess.run')
    def test_capture_stderr(self, mock_run):
        """Test capturing stderr output"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b""
        process_mock.stderr = b"Error message\n"
        process_mock.returncode = 0  # Success return code
        mock_run.return_value = process_mock

        adapter = ShellAdapter({"capture_stderr": True})
        adapter.command("echo 'Error message' >&2")  # Redirect to stderr
        result = adapter.execute()

        # Should capture stderr output
        self.assertEqual(result, "Error message")

    @patch('subprocess.run')
    def test_pipeline_commands(self, mock_run):
        """Test shell pipeline commands"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b"3\n"  # Count of lines containing 'a'
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = ShellAdapter({})
        adapter.command("echo -e 'apple\nbanana\norange\navocado' | grep 'a' | wc -l")
        result = adapter.execute()

        # Verify the pipeline command was executed
        mock_run.assert_called_once()
        self.assertEqual(result, "3")


if __name__ == "__main__":
    unittest.main()