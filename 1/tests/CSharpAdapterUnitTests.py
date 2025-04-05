# tests/test_csharp_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile

# Import the adapter to test
sys.path.append('..')
from adapters.CSharpAdapter import CSharpAdapter


class CSharpAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of CSharpAdapter"""
        adapter = CSharpAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    @patch('subprocess.run')
    def test_execute_code(self, mock_run):
        """Test executing a C# code snippet"""
        # Mock the subprocess.run return value
        process_mock = MagicMock()
        process_mock.stdout = b"Hello, C# World\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        csharp_code = """
        using System;
        
        class Program
        {
            static void Main()
            {
                Console.WriteLine("Hello, C# World");
            }
        }
        """

        adapter = CSharpAdapter({})
        adapter.code(csharp_code)
        result = adapter.execute()

        # Verify the code was executed
        mock_run.assert_called_once()
        self.assertTrue("dotnet" in mock_run.call_args[0][0][0])
        self.assertEqual(result, "Hello, C# World")

    @patch('subprocess.run')
    def test_execute_with_parameters(self, mock_run):
        """Test executing C# code with command-line arguments"""
        process_mock = MagicMock()
        process_mock.stdout = b"Argument: test_arg\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        csharp_code = """
        using System;
        
        class Program
        {
            static void Main(string[] args)
            {
                if (args.Length > 0)
                {
                    Console.WriteLine($"Argument: {args[0]}");
                }
            }
        }
        """

        adapter = CSharpAdapter({})
        adapter.code(csharp_code)
        adapter.args(["test_arg"])
        result = adapter.execute()

        # Verify args were passed correctly
        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        self.assertTrue("test_arg" in cmd_args)
        self.assertEqual(result, "Argument: test_arg")

    @patch('subprocess.run')
    def test_execute_file(self, mock_run):
        """Test executing a C# file"""
        test_file = os.path.join(self.test_dir, "test.cs")
        with open(test_file, 'w') as f:
            f.write("""
            using System;
            
            class Program
            {
                static void Main()
                {
                    Console.WriteLine("File executed");
                }
            }
            """)

        process_mock = MagicMock()
        process_mock.stdout = b"File executed\n"
        process_mock.returncode = 0
        mock_run.return_value = process_mock

        adapter = CSharpAdapter({})
        adapter.file(test_file)
        result = adapter.execute()

        # Verify the file was executed
        mock_run.assert_called_once()
        self.assertTrue(test_file in " ".join(mock_run.call_args[0][0]) or
                        (os.path.basename(test_file) in " ".join(mock_run.call_args[0][0])))
        self.assertEqual(result, "File executed")

        # Clean up
        os.remove(test_file)

    @patch('subprocess.run')
    def test_error_handling(self, mock_run):
        """Test handling of C# compilation/execution errors"""
        # Mock a failed subprocess.run
        process_mock = MagicMock()
        process_mock.stderr = b"(1,20): error CS0103: The name 'undefinedVar' does not exist in the current context\n"
        process_mock.returncode = 1
        mock_run.return_value = process_mock

        adapter = CSharpAdapter({})
        adapter.code("""
        using System;
        
        class Program
        {
            static void Main()
            {
                Console.WriteLine(undefinedVar);
            }
        }
        """)

        # Test if the adapter properly handles errors
        with self.assertRaises(Exception):
            adapter.execute()


if __name__ == "__main__":
    unittest.main()