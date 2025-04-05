# tests/test_utilities.py
import unittest
import sys
import tempfile
import os
import json
import yaml

# Import utilities to test
sys.path.append('..')
from utilities.ConfigManager import ConfigManager
from utilities.DataValidator import DataValidator
from utilities.Logger import Logger
from utilities.DataTransformer import DataTransformer


class ConfigManagerTest(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for config files
        self.temp_dir = tempfile.mkdtemp()

        # Sample config data
        self.config_data = {
            "app": {
                "name": "DataAdapter",
                "version": "1.0.0"
            },
            "adapters": {
                "json": {
                    "indent": 2
                },
                "rest": {
                    "timeout": 30,
                    "retries": 3
                }
            },
            "logging": {
                "level": "INFO",
                "file": "app.log"
            }
        }

        # Create config files
        self.json_config_path = os.path.join(self.temp_dir, "config.json")
        with open(self.json_config_path, 'w') as f:
            json.dump(self.config_data, f)

        self.yaml_config_path = os.path.join(self.temp_dir, "config.yaml")
        with open(self.yaml_config_path, 'w') as f:
            yaml.dump(self.config_data, f)

    def tearDown(self):
        # Clean up temp directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_load_json_config(self):
        """Test loading configuration from JSON file"""
        config_manager = ConfigManager()
        config_manager.load(self.json_config_path)

        # Verify config was loaded
        self.assertEqual(config_manager.get("app.name"), "DataAdapter")
        self.assertEqual(config_manager.get("adapters.json.indent"), 2)
        self.assertEqual(config_manager.get("logging.level"), "INFO")

    def test_load_yaml_config(self):
        """Test loading configuration from YAML file"""
        config_manager = ConfigManager()
        config_manager.load(self.yaml_config_path)

        # Verify config was loaded
        self.assertEqual(config_manager.get("app.name"), "DataAdapter")
        self.assertEqual(config_manager.get("adapters.rest.timeout"), 30)

    def test_get_config_with_default(self):
        """Test getting configuration with default value"""
        config_manager = ConfigManager()
        config_manager.load(self.json_config_path)

        # Get existing value
        self.assertEqual(config_manager.get("app.version"), "1.0.0")

        # Get non-existing value with default
        self.assertEqual(config_manager.get("app.description", "Default Description"), "Default Description")

    def test_set_config_value(self):
        """Test setting configuration value"""
        config_manager = ConfigManager()
        config_manager.load(self.json_config_path)

        # Set a new value
        config_manager.set("app.description", "Data Adapter Framework")
        self.assertEqual(config_manager.get("app.description"), "Data Adapter Framework")

        # Override existing value
        config_manager.set("app.version", "1.1.0")
        self.assertEqual(config_manager.get("app.version"), "1.1.0")

    def test_save_config(self):
        """Test saving configuration to file"""
        config_manager = ConfigManager()
        config_manager.load(self.json_config_path)

        # Modify config
        config_manager.set("app.version", "1.1.0")

        # Save to new file
        new_config_path = os.path.join(self.temp_dir, "new_config.json")
        config_manager.save(new_config_path)

        # Load the saved file and verify
        new_config = ConfigManager()
        new_config.load(new_config_path)
        self.assertEqual(new_config.get("app.version"), "1.1.0")

    def test_get_section(self):
        """Test getting a configuration section"""
        config_manager = ConfigManager()
        config_manager.load(self.json_config_path)

        # Get the adapters section
        adapters_config = config_manager.get_section("adapters")
        self.assertIsInstance(adapters_config, dict)
        self.assertEqual(adapters_config["json"]["indent"], 2)
        self.assertEqual(adapters_config["rest"]["timeout"], 30)


class DataValidatorTest(unittest.TestCase):
    def test_validate_type(self):
        """Test validating data types"""
        validator = DataValidator()

        # Test with valid types
        self.assertTrue(validator.validate_type(42, int))
        self.assertTrue(validator.validate_type("hello", str))
        self.assertTrue(validator.validate_type([1, 2, 3], list))
        self.assertTrue(validator.validate_type({"a": 1}, dict))

        # Test with invalid types
        self.assertFalse(validator.validate_type("42", int))
        self.assertFalse(validator.validate_type(42, str))

    def test_validate_required_fields(self):
        """Test validating required fields in a dictionary"""
        validator = DataValidator()

        # Data with all required fields
        data = {
            "id": 1,
            "name": "Test",
            "email": "test@example.com"
        }

        # Test with all required fields present
        self.assertTrue(validator.validate_required_fields(data, ["id", "name", "email"]))

        # Test with some required fields missing
        self.assertFalse(validator.validate_required_fields(data, ["id", "name", "phone"]))

    def test_validate_schema(self):
        """Test validating data against a schema"""
        validator = DataValidator()

        # Define a schema
        schema = {
            "id": {"type": int, "required": True},
            "name": {"type": str, "required": True},
            "email": {"type": str, "required": True},
            "age": {"type": int, "required": False}
        }

        # Valid data
        valid_data = {
            "id": 1,
            "name": "Test",
            "email": "test@example.com",
            "age": 30
        }

        # Missing required field
        invalid_data1 = {
            "id": 1,
            "name": "Test",
            "age": 30
        }

        # Wrong type
        invalid_data2 = {
            "id": "1",  # Should be int
            "name": "Test",
            "email": "test@example.com"
        }

        # Test validation
        self.assertTrue(validator.validate_schema(valid_data, schema))
        self.assertFalse(validator.validate_schema(invalid_data1, schema))
        self.assertFalse(validator.validate_schema(invalid_data2, schema))

    def test_validate_value_range(self):
        """Test validating numeric value ranges"""
        validator = DataValidator()

        # Test within range
        self.assertTrue(validator.validate_range(5, 1, 10))

        # Test at boundaries
        self.assertTrue(validator.validate_range(1, 1, 10))
        self.assertTrue(validator.validate_range(10, 1, 10))

        # Test outside range
        self.assertFalse(validator.validate_range(0, 1, 10))
        self.assertFalse(validator.validate_range(11, 1, 10))

    def test_validate_string_pattern(self):
        """Test validating string patterns with regex"""
        validator = DataValidator()

        # Email regex
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        # Test valid email
        self.assertTrue(validator.validate_pattern("test@example.com", email_pattern))

        # Test invalid email
        self.assertFalse(validator.validate_pattern("testexample.com", email_pattern))
        self.assertFalse(validator.validate_pattern("test@example", email_pattern))


class LoggerTest(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for logs
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        # Clean up
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        os.rmdir(self.temp_dir)

    def test_log_to_file(self):
        """Test logging messages to a file"""
        logger = Logger(self.log_file)

        # Log messages
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Check file exists
        self.assertTrue(os.path.exists(self.log_file))

        # Read log file
        with open(self.log_file, 'r') as f:
            content = f.read()

        # Check log content
        self.assertIn("INFO", content)
        self.assertIn("Info message", content)
        self.assertIn("WARNING", content)
        self.assertIn("Warning message", content)
        self.assertIn("ERROR", content)
        self.assertIn("Error message", content)

    def test_log_level_filtering(self):
        """Test log level filtering"""
        # Create logger with WARNING level
        logger = Logger(self.log_file, level="WARNING")

        # Log messages at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Read log file
        with open(self.log_file, 'r') as f:
            content = f.read()

        # Check log content - Debug and Info should be filtered out
        self.assertNotIn("DEBUG", content)
        self.assertNotIn("Debug message", content)
        self.assertNotIn("INFO", content)
        self.assertNotIn("Info message", content)
        self.assertIn("WARNING", content)
        self.assertIn("Warning message", content)
        self.assertIn("ERROR", content)
        self.assertIn("Error message", content)


class DataTransformerTest(unittest.TestCase):
    def test_transform_dict_to_list(self):
        """Test transforming dict to list of key-value pairs"""
        transformer = DataTransformer()

        data = {
            "id": 1,
            "name": "Test",
            "active": True
        }

        result = transformer.dict_to_list(data)
        expected = [
            {"key": "id", "value": 1},
            {"key": "name", "value": "Test"},
            {"key": "active", "value": True}
        ]

        # Sort both lists to ensure consistent order for comparison
        result = sorted(result, key=lambda x: x["key"])
        expected = sorted(expected, key=lambda x: x["key"])

        self.assertEqual(result, expected)

    def test_transform_list_to_dict(self):
        """Test transforming list of key-value pairs to dict"""
        transformer = DataTransformer()

        data = [
            {"key": "id", "value": 1},
            {"key": "name", "value": "Test"},
            {"key": "active", "value": True}
        ]

        result = transformer.list_to_dict(data)
        expected = {
            "id": 1,
            "name": "Test",
            "active": True
        }

        self.assertEqual(result, expected)

    def test_flatten_nested_dict(self):
        """Test flattening a nested dictionary"""
        transformer = DataTransformer()

        nested_data = {
            "user": {
                "id": 1,
                "name": "Test",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown"
                }
            },
            "status": "active"
        }

        result = transformer.flatten_dict(nested_data)
        expected = {
            "user.id": 1,
            "user.name": "Test",
            "user.address.street": "123 Main St",
            "user.address.city": "Anytown",
            "status": "active"
        }

        self.assertEqual(result, expected)

    def test_nest_flattened_dict(self):
        """Test nesting a flattened dictionary"""
        transformer = DataTransformer()

        flat_data = {
            "user.id": 1,
            "user.name": "Test",
            "user.address.street": "123 Main St",
            "user.address.city": "Anytown",
            "status": "active"
        }

        result = transformer.nest_dict(flat_data)
        expected = {
            "user": {
                "id": 1,
                "name": "Test",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown"
                }
            },
            "status": "active"
        }

        self.assertEqual(result, expected)

    def test_transform_json_to_xml(self):
        """Test transforming JSON to XML string"""
        transformer = DataTransformer()

        json_data = {
            "users": {
                "user": [
                    {
                        "@id": "1",
                        "name": "John",
                        "email": "john@example.com"
                    },
                    {
                        "@id": "2",
                        "name": "Jane",
                        "email": "jane@example.com"
                    }
                ]
            }
        }

        xml_result = transformer.json_to_xml(json_data)

        # Basic validation of XML result
        self.assertTrue(xml_result.startswith('<?xml version="1.0" ?>'))
        self.assertTrue("<users>" in xml_result)
        self.assertTrue('<user id="1">' in xml_result or '<user id="1"/>' in xml_result)
        self.assertTrue("<name>John</name>" in xml_result)
        self.assertTrue("<email>jane@example.com</email>" in xml_result)

    def test_transform_xml_to_json(self):
        """Test transforming XML to JSON object"""
        transformer = DataTransformer()

        xml_data = '''<?xml version="1.0" ?>
        <users>
            <user id="1">
                <name>John</name>
                <email>john@example.com</email>
            </user>
            <user id="2">
                <name>Jane</name>
                <email>jane@example.com</email>
            </user>
        </users>'''

        json_result = transformer.xml_to_json(xml_data)

        # Validate JSON structure
        self.assertTrue("users" in json_result)
        self.assertTrue("user" in json_result["users"])
        self.assertEqual(len(json_result["users"]["user"]), 2)
        self.assertEqual(json_result["users"]["user"][0]["@id"], "1")
        self.assertEqual(json_result["users"]["user"][1]["name"], "Jane")


if __name__ == "__main__":
    unittest.main()