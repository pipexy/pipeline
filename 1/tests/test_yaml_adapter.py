# tests/test_yaml_adapter.py (continued)
adapter = YAMLAdapter({})
adapter.parse_file(test_file)
result = adapter.execute()

# Verify the YAML was parsed
self.assertIsNotNone(result)
self.assertIsInstance(result, dict)
self.assertEqual(len(result["people"]), 2)

# Clean up
os.remove(test_file)


def test_query_path(self):
    """Test querying YAML with path expressions"""
    adapter = YAMLAdapter({})
    adapter.parse_string(self.test_yaml)
    adapter.query_path("people[1].name")
    result = adapter.execute()

    # Verify the query result
    self.assertEqual(result, "Jane Smith")


def test_nested_query(self):
    """Test querying nested YAML structures"""
    adapter = YAMLAdapter({})
    adapter.parse_string(self.test_yaml)
    adapter.query_path("people[0].contact.email")
    result = adapter.execute()

    # Verify the nested query result
    self.assertEqual(result, "john@example.com")


def test_modify_value(self):
    """Test modifying YAML values"""
    adapter = YAMLAdapter({})
    adapter.parse_string(self.test_yaml)

    # Modify a value
    data = adapter.execute()
    data["people"][0]["age"] = 31

    # Query the modified value
    adapter.query_path("people[0].age")
    result = adapter.execute()
    self.assertEqual(result, 31)


def test_to_string(self):
    """Test converting YAML to string"""
    adapter = YAMLAdapter({})
    adapter.parse_string(self.test_yaml)
    adapter.to_string()
    result = adapter.execute()

    # Verify it's a string representation of the YAML
    self.assertIsInstance(result, str)

    # Parse it back to verify it's valid YAML
    parsed = yaml.safe_load(result)
    self.assertEqual(parsed["people"][0]["name"], "John Doe")


def test_create_object(self):
    """Test creating a new YAML object"""
    adapter = YAMLAdapter({})
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
    """Test filtering YAML arrays"""
    adapter = YAMLAdapter({})
    adapter.parse_string(self.test_yaml)

    # Get people over 25
    data = adapter.execute()
    filtered = [p for p in data["people"] if p["age"] > 25]

    # Verify filter results
    self.assertEqual(len(filtered), 1)
    self.assertEqual(filtered[0]["name"], "John Doe")


def test_write_to_file(self):
    """Test writing YAML to a file"""
    adapter = YAMLAdapter({})
    adapter.parse_string(self.test_yaml)
    data = adapter.execute()

    # Modify data
    data["organization"] = "Updated Company"

    # Write to file
    output_file = os.path.join(self.test_dir, "output.yaml")
    adapter.write_file(output_file)
    adapter.execute()

    # Verify file was written
    self.assertTrue(os.path.exists(output_file))

    # Read it back
    with open(output_file, 'r') as f:
        content = f.read()

    self.assertTrue("Updated Company" in content)

    # Clean up
    os.remove(output_file)


def test_error_handling(self):
    """Test handling YAML parsing errors"""
    # Invalid YAML
    invalid_yaml = "array: [unclosed"

    adapter = YAMLAdapter({})
    adapter.parse_string(invalid_yaml)

    # Should raise an exception
    with self.assertRaises(Exception):
        adapter.execute()


if __name__ == "__main__":
    unittest.main()