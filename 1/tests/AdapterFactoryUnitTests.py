# tests/test_adapter_factory.py (continued)
def test_create_unknown_adapter(self):
    """Test creating an unknown adapter type"""
    factory = AdapterFactory()

    # Should raise an exception for unknown adapter type
    with self.assertRaises(ValueError):
        factory.create_adapter("unknown_type", {})


def test_register_custom_adapter(self):
    """Test registering and creating a custom adapter"""

    # Create a simple custom adapter class
    class CustomAdapter:
        def __init__(self, config):
            self.config = config
            self.name = "custom"

    # Register the adapter
    factory = AdapterFactory()
    factory.register_adapter("custom", CustomAdapter)

    # Create the custom adapter
    adapter = factory.create_adapter("custom", {"test": "value"})

    # Verify
    self.assertIsNotNone(adapter)
    self.assertIsInstance(adapter, CustomAdapter)
    self.assertEqual(adapter.config["test"], "value")


def test_adapter_with_default_config(self):
    """Test creating adapter with default config values"""
    factory = AdapterFactory()

    # Add default config for REST adapter
    default_config = {
        "timeout": 30,
        "retry_count": 3,
        "headers": {"Accept": "application/json"}
    }

    # Create adapter with partial config that should be merged with defaults
    partial_config = {
        "base_url": "https://api.example.com",
        "headers": {"Content-Type": "application/json"}
    }

    # Create with default config
    adapter = factory.create_adapter("rest", partial_config, default_config)

    # Verify merged config
    self.assertEqual(adapter.config["base_url"], "https://api.example.com")
    self.assertEqual(adapter.config["timeout"], 30)
    self.assertEqual(adapter.config["retry_count"], 3)
    # Headers should be merged
    self.assertEqual(adapter.config["headers"]["Content-Type"], "application/json")
    self.assertEqual(adapter.config["headers"]["Accept"], "application/json")


def test_create_multiple_adapters(self):
    """Test creating multiple different adapters"""
    factory = AdapterFactory()

    # Create multiple adapters
    json_adapter = factory.create_adapter("json", {})
    yaml_adapter = factory.create_adapter("yaml", {})
    rest_adapter = factory.create_adapter("rest", {"base_url": "https://api.example.com"})

    # Verify all were created correctly
    self.assertIsInstance(json_adapter, JSONAdapter)
    self.assertIsInstance(yaml_adapter, YAMLAdapter)
    self.assertIsInstance(rest_adapter, RESTAdapter)


if __name__ == "__main__":
    unittest.main()