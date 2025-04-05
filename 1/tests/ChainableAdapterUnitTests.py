# tests/test_chainable_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys

# Import the adapter to test
sys.path.append('..')
from adapters.ChainableAdapter import ChainableAdapter
from adapters.BashAdapter import BashAdapter  # For testing chaining


class ChainableAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        pass

    def test_initialization(self):
        """Test basic initialization of ChainableAdapter"""
        adapter = ChainableAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    def test_adapter_chaining(self):
        """Test chaining multiple adapters"""
        # Create first adapter that outputs a value
        first_adapter = BashAdapter({})
        first_adapter.command("echo 'hello'")

        # Create second adapter that processes the output
        second_adapter = BashAdapter({})
        second_adapter.command("tr 'a-z' 'A-Z'")  # Convert to uppercase

        # Chain them
        chainable = ChainableAdapter({})
        chainable.chain([first_adapter, second_adapter])

        # Mock the execution of both adapters
        with patch.object(first_adapter, 'execute', return_value="hello\n"):
            with patch.object(second_adapter, 'execute', return_value="HELLO\n"):
                result = chainable.execute()

                # Verify the result is the processed output
                self.assertEqual(result, "HELLO\n")

    def test_empty_chain(self):
        """Test an empty chain"""
        chainable = ChainableAdapter({})
        chainable.chain([])

        # Should not raise an error but return None
        result = chainable.execute()
        self.assertIsNone(result)

    def test_single_adapter_chain(self):
        """Test a chain with a single adapter"""
        adapter = BashAdapter({})
        adapter.command("echo 'single'")

        chainable = ChainableAdapter({})
        chainable.chain([adapter])

        with patch.object(adapter, 'execute', return_value="single\n"):
            result = chainable.execute()
            self.assertEqual(result, "single\n")

    def test_error_propagation(self):
        """Test error propagation in a chain"""
        first_adapter = BashAdapter({})
        first_adapter.command("echo 'start'")

        second_adapter = BashAdapter({})
        second_adapter.command("invalid_command")  # This will fail

        chainable = ChainableAdapter({})
        chainable.chain([first_adapter, second_adapter])

        with patch.object(first_adapter, 'execute', return_value="start\n"):
            with patch.object(second_adapter, 'execute', side_effect=Exception("Command failed")):
                # The error should propagate
                with self.assertRaises(Exception):
                    chainable.execute()

    def test_data_transformation(self):
        """Test data transformation between adapters"""
        # First adapter outputs JSON
        first_adapter = BashAdapter({})
        first_adapter.command("echo '{\"name\": \"test\"}'")

        # Second adapter expects and transforms JSON
        second_adapter = BashAdapter({})
        second_adapter.command("jq '.name | ascii_upcase'")

        chainable = ChainableAdapter({})
        chainable.chain([first_adapter, second_adapter])

        with patch.object(first_adapter, 'execute', return_value='{"name": "test"}\n'):
            with patch.object(second_adapter, 'execute', return_value='"TEST"\n'):
                result = chainable.execute()
                self.assertEqual(result, '"TEST"\n')


if __name__ == "__main__":
    unittest.main()