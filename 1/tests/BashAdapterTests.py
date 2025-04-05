# tests/test_bash_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile

# Import the adapter to test
sys.path.append('..')
from adapters.BashAdapter import BashAdapter


class BashAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_dir = tempfile.mkdtemp()
        # Any other setup needed

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of BashAdapter"""
        adapter = BashAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    def test_execute_command(self):
        """Test executing a simple bash command"""
        adapter = BashAdapter({})
        adapter.command("echo 'test'")
        result = adapter.execute()
        self.assertEqual(result.strip(), "test")

    def test_error_handling(self):
        """Test handling of command errors"""
        adapter = BashAdapter({})
        adapter.command("invalid_command")
        # Test how the adapter handles errors

    # Additional tests for specific BashAdapter functionality


if __name__ == "__main__":
    unittest.main()