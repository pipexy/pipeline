# tests/test_go_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile

# Import the adapter to test
sys.path.append('..')
from adapters.GoAdapter import GoAdapter


class GoAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of GoAdapter"""
        adapter = GoAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    @patch('subprocess.run')
    def test_execute_code(self, mock_run):
        """Test executing a Go code snippet"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b"Hello, Go World\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        go_code = """
        package main
        
        import "fmt"
        
        func main() {
            fmt.Println("Hello, Go World")
        }
        """

        adapter = GoAdapter({})
        adapter.code(go_code)
        result = adapter.execute()

        # Verify the code was executed
        mock_run.assert_called_once()
        self.assertTrue("go run" in " ".join(mock_run.call_args[0][0]))
        self.assertEqual(result, "Hello, Go World")

    @patch('subprocess.run')
    def test_execute_with_parameters(self, mock_run):
        """Test executing Go code with command-line arguments"""
        process_mock = MagicMock()
        process_mock.stdout = b"Argument: test_arg\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        go_code = """
        package main
        
        import (
            "fmt"
            "os"
        )
        
        func main() {
            if len(os.Args) > 1 {
                fmt.Printf("Argument: %s\\n", os.Args[1])
            }
        }
        """

        adapter = GoAdapter({})
        adapter.code(go_code)
        adapter.args(["test_arg"])
        result = adapter.execute()

        # Verify args were passed correctly
        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        self.assertTrue("test_arg" in cmd_args)
        self.assertEqual(result, "Argument: test_arg")

    @patch('subprocess.run')
    def test_execute_file(self, mock_run):
        """Test executing a Go file"""
        test_file = os.path.join(self.test_dir, "test.go")
        with open(test_file, 'w') as f:
            f.write("""
            package main
            
            import "fmt"
            
            func main() {
                fmt.Println("File executed")
            }
            """)

        process_mock = MagicMock()
        process_mock.stdout = b"File executed\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = GoAdapter({})
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
        """Test handling of Go compilation/execution errors"""
        # Mock a failed subprocess.run
        process_mock = MagicMock()
        process_mock.stderr = b"./main.go:6:14: undefined: undefinedVar\n"
        process_mock.returncode = 2
        mock_run.return_value = process_mock

        adapter = GoAdapter({})
        adapter.code("""
        package main
        
        import "fmt"
        
        func main() {
            fmt.Println(undefinedVar)
        }
        """)

        # Test if the adapter properly handles errors
        with self.assertRaises(Exception):
            adapter.execute()


if __name__ == "__main__":
    unittest.main()