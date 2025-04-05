# tests/test_javascript_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile

# Import the adapter to test
sys.path.append('..')
from adapters.JavaScriptAdapter import JavaScriptAdapter


class JavaScriptAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_dir = tempfile.mkdtemp()
        self.test_script = "function greet(name) { return 'Hello, ' + name; }"

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of JavaScriptAdapter"""
        adapter = JavaScriptAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    @patch('subprocess.run')
    def test_execute_inline_script(self, mock_run):
        """Test executing an inline JavaScript script"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b"Hello, World\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = JavaScriptAdapter({})
        adapter.script("console.log('Hello, World');")
        result = adapter.execute()

        # Verify the script was executed
        mock_run.assert_called_once()
        self.assertTrue("node" in mock_run.call_args[0][0][0])
        self.assertEqual(result, "Hello, World")

    @patch('subprocess.run')
    def test_execute_with_parameters(self, mock_run):
        """Test executing JavaScript with parameters"""
        process_mock = MagicMock()
        process_mock.stdout = b"42\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = JavaScriptAdapter({})
        adapter.script("const x = parseInt(process.argv[2]); console.log(x + 2);")
        adapter.args(["40"])
        result = adapter.execute()

        # Verify args were passed correctly
        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        self.assertTrue("40" in cmd_args)
        self.assertEqual(result, "42")

    @patch('subprocess.run')
    def test_execute_file(self, mock_run):
        """Test executing a JavaScript file"""
        test_file = os.path.join(self.test_dir, "test.js")
        with open(test_file, 'w') as f:
            f.write("console.log('File executed');")

        process_mock = MagicMock()
        process_mock.stdout = b"File executed\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = JavaScriptAdapter({})
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
        """Test handling of JavaScript errors"""
        # Mock a failed subprocess.run
        process_mock = MagicMock()
        process_mock.stderr = b"ReferenceError: invalidVariable is not defined\n"
        process_mock.returncode = 1
        mock_run.return_value = process_mock

        adapter = JavaScriptAdapter({})
        adapter.script("console.log(invalidVariable);")

        # Test if the adapter properly handles errors
        with self.assertRaises(Exception):
            adapter.execute()


if __name__ == "__main__":
    unittest.main()