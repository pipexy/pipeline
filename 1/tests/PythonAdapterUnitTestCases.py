# tests/test_python_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile

# Import the adapter to test
sys.path.append('..')
from adapters.PythonAdapter import PythonAdapter


class PythonAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of PythonAdapter"""
        adapter = PythonAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    @patch('subprocess.run')
    def test_execute_script(self, mock_run):
        """Test executing a Python script"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b"Hello, Python World\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = PythonAdapter({})
        adapter.script("print('Hello, Python World')")
        result = adapter.execute()

        # Verify the script was executed
        mock_run.assert_called_once()
        self.assertTrue("python" in mock_run.call_args[0][0][0])
        self.assertEqual(result, "Hello, Python World")

    def test_exec_method(self):
        """Test the exec method for direct Python execution"""
        adapter = PythonAdapter({})
        adapter.script("result = 2 + 3")

        # Using a patch to capture stdout
        with patch('sys.stdout') as mock_stdout:
            mock_stdout.write = MagicMock()
            result = adapter.exec()

            # Should have variables defined in local scope
            self.assertEqual(result.get('result'), 5)

    @patch('subprocess.run')
    def test_execute_with_arguments(self, mock_run):
        """Test executing Python with command line arguments"""
        process_mock = MagicMock()
        process_mock.stdout = b"Argument: test_arg\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = PythonAdapter({})
        adapter.script("import sys; print(f'Argument: {sys.argv[1]}')")
        adapter.args(["test_arg"])
        result = adapter.execute()

        # Verify args were passed correctly
        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        self.assertTrue("test_arg" in cmd_args)
        self.assertEqual(result, "Argument: test_arg")

    @patch('subprocess.run')
    def test_file_execution(self, mock_run):
        """Test executing a Python file"""
        test_file = os.path.join(self.test_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("print('File executed')")

        process_mock = MagicMock()
        process_mock.stdout = b"File executed\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = PythonAdapter({})
        adapter.file(test_file)
        result = adapter.execute()

        # Verify the file was executed
        mock_run.assert_called_once()
        self.assertTrue(test_file in " ".join(mock_run.call_args[0][0]))
        self.assertEqual(result, "File executed")

        # Clean up
        os.remove(test_file)

    @patch('subprocess.run')
    def test_error_handling(self, mock_run):
        """Test handling of Python errors"""
        # Mock a failed subprocess.run
        process_mock = MagicMock()
        process_mock.stderr = b"NameError: name 'undefined_var' is not defined\n"
        process_mock.returncode = 1
        mock_run.return_value = process_mock

        adapter = PythonAdapter({})
        adapter.script("print(undefined_var)")

        # Test if the adapter properly handles errors
        with self.assertRaises(Exception):
            adapter.execute()

    def test_environment_variables(self):
        """Test setting environment variables"""
        adapter = PythonAdapter({})
        adapter.script("import os; print(os.environ.get('TEST_VAR'))")
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


if __name__ == "__main__":
    unittest.main()