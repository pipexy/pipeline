# tests/test_json_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
import json

# Import the adapter to test
sys.path.append('..')
from adapters.JSONAdapter import JSONAdapter


class JSONAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_dir = tempfile.mkdtemp()
        self.test_json = """
        {
            "people": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "age": 30,
                    "contact": {
                        "email": "john@example.com",
                        "phone": "555-1234"
                    }
                },
                {
                    "id": 2,
                    "name": "Jane Smith",
                    "age": 25,
                    "contact": {
                        "email": "jane@example.com",
                        "phone": "555-5678"
                    }
                }
            ],
            "organization": "Test Company"
        }
        """

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of JSONAdapter"""
        adapter = JSONAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    def test_parse_string(self):
        """Test parsing JSON from a string"""
        adapter = JSONAdapter({})
        adapter.parse_string(self.test_json)
        result = adapter.execute()

        # Verify the JSON was parsed
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["people"]), 2)
        self.assertEqual(result["people"][0]["name"], "John Doe")
        self.assertEqual(result["organization"], "Test Company")

    def test_parse_file(self):
        """Test parsing JSON from a file"""
        # Create a test JSON file
        test_file = os.path.join(self.test_dir, "test.json")
        with open(test_file, 'w') as f:
            f.write(self.test_json)

        adapter = JSONAdapter({})
        adapter.parse_file(test_file)
        result = adapter.execute()

        # Verify the JSON was parsed
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["people"]), 2)

        # Clean up
        os.remove(test_file)

    def test_query_path(self):
        """Test querying JSON with path expressions"""
        adapter = JSONAdapter({})
        adapter.parse_string(self.test_json)
        adapter.query_path("people[1].name")
        result = adapter.execute()

        # Verify the query result
        self.assertEqual(result, "Jane Smith")

    def test_nested_query(self):
        """Test querying nested JSON structures"""
        adapter = JSONAdapter({})
        adapter.parse_string(self.test_json)
        adapter.query_path("people[0].contact.email")
        result = adapter.execute()

        # Verify the nested query result
        self.assertEqual(result, "john@example.com")

    def test_modify_value(self):
        """Test modifying JSON values"""
        adapter = JSONAdapter({})
        adapter.parse_string(self.test_json)

        # Modify a value
        data = adapter.execute()
        data["people"][0]["age"] = 31

        # Query the modified value
        adapter.query_path("people[0].age")
        result = adapter.execute()
        self.assertEqual(result, 31)

    def test_to_string(self):
        """Test converting JSON to string"""
        adapter = JSONAdapter({})
        adapter.parse_string(self.test_json)
        adapter.to_string()
        result = adapter.execute()

        # Verify it's a string representation of the JSON
        self.assertIsInstance(result, str)

        # Parse it back to verify it's valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["people"][0]["name"], "John Doe")

    def test_create_object(self):
        """Test creating a new JSON object"""
        adapter = JSONAdapter({})
        adapter.create_object({
            "id": 3,
            "name": "Bob Johnson",
            "age": 40,
            "contact": {
                "email": "bob@example.com",
                "phone": "555-9012"
            }
        })
        result = adapter.execute()

        # Verify the created object
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Bob Johnson")
        self.assertEqual(result["contact"]["email"], "bob@example.com")

    def test_filter_array(self):
        """Test filtering JSON arrays"""
        adapter = JSONAdapter({})
        adapter.parse_string(self.test_json)

        # Get people over 25
        data = adapter.execute()
        filtered = [p for p in data["people"] if p["age"] > 25]

        # Verify filter results
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["name"], "John Doe")

    def test_error_handling(self):
        """Test handling JSON parsing errors"""
        # Invalid JSON
        invalid_json = "{unclosed: object"

        adapter = JSONAdapter({})
        adapter.parse_string(invalid_json)

        # Should raise an exception
        with self.assertRaises(Exception):
            adapter.execute()


if __name__ == "__main__":
    unittest.main()