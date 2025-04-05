# tests/test_integration.py
import unittest
import sys
import os
import tempfile
import json
import yaml
import csv
import xml.etree.ElementTree as ET

# Import necessary components
sys.path.append('..')
from adapters.JSONAdapter import JSONAdapter
from adapters.YAMLAdapter import YAMLAdapter
from adapters.CSVAdapter import CSVAdapter
from adapters.XMLAdapter import XMLAdapter
from adapters.AdapterFactory import AdapterFactory
from transformers.Transformer import Transformer
from core.DataAdapterManager import DataAdapterManager
from utilities.ConfigManager import ConfigManager


class IntegrationTest(unittest.TestCase):
    """Integration tests for testing multiple adapters working together"""

    def setUp(self):
        # Create temp directory for test files
        self.temp_dir = tempfile.mkdtemp()

        # Create sample data files
        self.json_data = {
            "users": [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
            ],
            "settings": {
                "active": True,
                "version": "1.0"
            }
        }

        self.json_file = os.path.join(self.temp_dir, "data.json")
        with open(self.json_file, 'w') as f:
            json.dump(self.json_data, f)

        self.yaml_data = {
            "products": [
                {"id": 101, "name": "Laptop", "price": 999.99},
                {"id": 102, "name": "Smartphone", "price": 499.99}
            ],
            "categories": ["Electronics", "Computers", "Mobile"]
        }

        self.yaml_file = os.path.join(self.temp_dir, "data.yaml")
        with open(self.yaml_file, 'w') as f:
            yaml.dump(self.yaml_data, f)

        self.csv_data = [
            ["id", "name", "department", "salary"],
            ["1", "Alice", "Engineering", "75000"],
            ["2", "Bob", "Marketing", "65000"],
            ["3", "Charlie", "Finance", "85000"]
        ]

        self.csv_file = os.path.join(self.temp_dir, "data.csv")
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in self.csv_data:
                writer.writerow(row)

        self.xml_data = """
        <company>
            <department name="Engineering">
                <employee id="1">
                    <name>David</name>
                    <position>Developer</position>
                </employee>
                <employee id="2">
                    <name>Emma</name>
                    <position>Designer</position>
                </employee>
            </department>
            <department name="HR">
                <employee id="3">
                    <name>Frank</name>
                    <position>Manager</position>
                </employee>
            </department>
        </company>
        """

        self.xml_file = os.path.join(self.temp_dir, "data.xml")
        with open(self.xml_file, 'w') as f:
            f.write(self.xml_data)

        # Config file
        self.config_data = {
            "adapters": {
                "json": {
                    "indent": 2
                },
                "yaml": {
                    "default_flow_style": False
                },
                "csv": {
                    "delimiter": ",",
                    "quotechar": "\""
                },
                "xml": {
                    "encoding": "utf-8"
                }
            },
            "transformers": {
                "json_to_yaml": {
                    "source": "json",
                    "target": "yaml"
                },
                "csv_to_json": {
                    "source": "csv",
                    "target": "json"
                }
            }
        }

        self.config_file = os.path.join(self.temp_dir, "config.json")
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f)

    def tearDown(self):
        # Clean up temp directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_json_to_yaml_conversion(self):
        """Test converting JSON data to YAML format"""
        # Create adapters
        json_adapter = JSONAdapter({"indent": 2})
        yaml_adapter = YAMLAdapter({"default_flow_style": False})

        # Load JSON data
        json_adapter.parse_file(self.json_file)
        json_data = json_adapter.execute()

        # Convert to YAML
        yaml_adapter.from_dict(json_data)
        yaml_output = yaml_adapter.execute()

        # Export to file
        yaml_output_file = os.path.join(self.temp_dir, "output.yaml")
        with open(yaml_output_file, 'w') as f:
            f.write(yaml_output)

        # Load the exported YAML and verify
        with open(yaml_output_file, 'r') as f:
            loaded_yaml = yaml.safe_load(f)

        # Verify data was preserved
        self.assertEqual(loaded_yaml["users"][0]["name"], "John Doe")
        self.assertEqual(loaded_yaml["settings"]["version"], "1.0")

    def test_csv_to_json_conversion(self):
        """Test converting CSV data to JSON format"""
        # Create adapters
        csv_adapter = CSVAdapter({"delimiter": ",", "quotechar": '"'})
        json_adapter = JSONAdapter({"indent": 2})

        # Load CSV data
        csv_adapter.parse_file(self.csv_file)
        csv_data = csv_adapter.execute()

        # Convert to JSON
        json_adapter.from_dict({"employees": csv_data})
        json_output = json_adapter.execute()

        # Export to file
        json_output_file = os.path.join(self.temp_dir, "output.json")
        with open(json_output_file, 'w') as f:
            f.write(json_output)

        # Load the exported JSON and verify
        with open(json_output_file, 'r') as f:
            loaded_json = json.load(f)

        # Verify data was preserved
        self.assertEqual(loaded_json["employees"][0]["name"], "Alice")
        self.assertEqual(loaded_json["employees"][2]["department"], "Finance")

    def test_xml_to_json_conversion(self):
        """Test converting XML data to JSON format"""
        # Create adapters
        xml_adapter = XMLAdapter({"encoding": "utf-8"})
        json_adapter = JSONAdapter({"indent": 2})

        # Load XML data
        xml_adapter.parse_file(self.xml_file)
        xml_root = xml_adapter.execute()

        # Convert XML to dict
        xml_dict = {}
        xml_dict["company"] = {"departments": []}

        for dept in xml_root.findall('department'):
            department = {
                "name": dept.get('name'),
                "employees": []
            }

            for emp in dept.findall('employee'):
                employee = {
                    "id": emp.get('id'),
                    "name": emp.find('name').text,
                    "position": emp.find('position').text
                }
                department["employees"].append(employee)

            xml_dict["company"]["departments"].append(department)

        # Convert to JSON
        json_adapter.from_dict(xml_dict)
        json_output = json_adapter.execute()

        # Export to file
        json_output_file = os.path.join(self.temp_dir, "output.json")
        with open(json_output_file, 'w') as f:
            f.write(json_output)

        # Load the exported JSON and verify
        with open(json_output_file, 'r') as f:
            loaded_json = json.load(f)

        # Verify data was preserved
        self.assertEqual(loaded_json["company"]["departments"][0]["name"], "Engineering")
        self.assertEqual(loaded_json["company"]["departments"][1]["employees"][0]["name"], "Frank")

    def test_adapter_factory(self):
        """Test using adapter factory to create and use multiple adapters"""
        factory = AdapterFactory()

        # Create adapters
        json_adapter = factory.create_adapter("json", {"indent": 2})
        yaml_adapter = factory.create_adapter("yaml", {"default_flow_style": False})
        csv_adapter = factory.create_adapter("csv", {"delimiter": ",", "quotechar": '"'})

        # Load data with each adapter
        json_adapter.parse_file(self.json_file)
        json_data = json_adapter.execute()

        yaml_adapter.parse_file(self.yaml_file)
        yaml_data = yaml_adapter.execute()

        csv_adapter.parse_file(self.csv_file)
        csv_data = csv_adapter.execute()

        # Verify each adapter loaded data correctly
        self.assertEqual(json_data["users"][0]["name"], "John Doe")
        self.assertEqual(yaml_data["products"][1]["name"], "Smartphone")
        self.assertEqual(csv_data[1]["name"], "Alice")

    def test_data_adapter_manager(self):
        """Test using DataAdapterManager to coordinate multiple adapters"""
        # Configure manager with config file
        config_manager = ConfigManager()
        config_manager.load(self.config_file)

        # Create adapter manager
        manager = DataAdapterManager(config_manager)

        # Register adapters
        manager.register_adapter("json", JSONAdapter)
        manager.register_adapter("yaml", YAMLAdapter)
        manager.register_adapter("csv", CSVAdapter)
        manager.register_adapter("xml", XMLAdapter)

        # Load data sources
        manager.load_source("users", "json", self.json_file)
        manager.load_source("products", "yaml", self.yaml_file)
        manager.load_source("employees", "csv", self.csv_file)

        # Retrieve data
        users = manager.get_data("users")
        products = manager.get_data("products")
        employees = manager.get_data("employees")

        # Verify data was loaded
        self.assertEqual(users["users"][0]["name"], "John Doe")
        self.assertEqual(products["products"][0]["name"], "Laptop")
        self.assertEqual(employees[1]["name"], "Alice")

        # Export data in a different format
        export_file = os.path.join(self.temp_dir, "users.yaml")
        manager.export_data("users", "yaml", export_file)

        # Verify exported file
        with open(export_file, 'r') as f:
            exported_data = yaml.safe_load(f)

        self.assertEqual(exported_data["users"][1]["name"], "Jane Smith")


class TransformerTest(unittest.TestCase):
    """Tests for the data transformation functionality"""

    def setUp(self):
        # Create sample data
        self.json_data = {
            "users": [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
            ]
        }

        self.csv_data = [
            {"id": "1", "name": "Alice", "department": "Engineering", "salary": "75000"},
            {"id": "2", "name": "Bob", "department": "Marketing", "salary": "65000"},
            {"id": "3", "name": "Charlie", "department": "Finance", "salary": "85000"}
        ]

    def test_transform_json_to_csv(self):
        """Test transforming JSON data to CSV format"""
        transformer = Transformer()

        # Define transformation
        def json_to_csv(source_data):
            result = []
            # Extract headers
            if len(source_data["users"]) > 0:
                headers = {}
                for key in source_data["users"][0].keys():
                    headers[key] = key
                result.append(headers)

            # Add data rows
            for user in source_data["users"]:
                result.append(user)

            return result

        # Register transformation
        transformer.register_transformation("json_to_csv", json_to_csv)

        # Apply transformation
        result = transformer.transform("json_to_csv", self.json_data)

        # Verify result
        self.assertEqual(len(result), 3)  # Headers + 2 users
        self.assertEqual(result[0]["id"], "id")
        self.assertEqual(result[1]["name"], "John Doe")
        self.assertEqual(result[2]["email"], "jane@example.com")

    def test_transform_csv_to_json(self):
        """Test transforming CSV data to JSON format"""
        transformer = Transformer()

        # Define transformation
        def csv_to_json(source_data):
            return {
                "employees": source_data,
                "metadata": {
                    "count": len(source_data),
                    "departments": list(set(row["department"] for row in source_data))
                }
            }

        # Register transformation
        transformer.register_transformation("csv_to_json", csv_to_json)

        # Apply transformation
        result = transformer.transform("csv_to_json", self.csv_data)

        # Verify result
        self.assertEqual(len(result["employees"]), 3)
        self.assertEqual(result["employees"][0]["name"], "Alice")
        self.assertEqual(result["metadata"]["count"], 3)
        self.assertIn("Engineering", result["metadata"]["departments"])
        self.assertIn("Marketing", result["metadata"]["departments"])
        self.assertIn("Finance", result["metadata"]["departments"])

    def test_chained_transformations(self):
        """Test applying multiple transformations in sequence"""
        transformer = Transformer()

        # Define first transformation: Filter users by ID > 1
        def filter_users(source_data):
            return {
                "users": [user for user in source_data["users"] if user["id"] > 1]
            }

        # Define second transformation: Add a status field
        def add_status(source_data):
            for user in source_data["users"]:
                user["status"] = "active"
            return source_data

        # Register transformations
        transformer.register_transformation("filter_users", filter_users)
        transformer.register_transformation("add_status", add_status)

        # Apply chained transformations
        intermediate = transformer.transform("filter_users", self.json_data)
        result = transformer.transform("add_status", intermediate)

        # Verify result
        self.assertEqual(len(result["users"]), 1)
        self.assertEqual(result["users"][0]["name"], "Jane Smith")
        self.assertEqual(result["users"][0]["status"], "active")

    def test_transform_with_parameters(self):
        """Test transformations with additional parameters"""
        transformer = Transformer()

        # Define parameterized transformation
        def filter_by_field(source_data, field, value):
            return {
                "users": [user for user in source_data["users"] if user[field] == value]
            }

        # Register transformation
        transformer.register_transformation("filter_by_field", filter_by_field)

        # Apply transformation with parameters
        result = transformer.transform("filter_by_field", self.json_data, field="id", value=1)

        # Verify result
        self.assertEqual(len(result["users"]), 1)
        self.assertEqual(result["users"][0]["name"], "John Doe")


class PerformanceTest(unittest.TestCase):
    """Performance tests for adapters with larger datasets"""

    def setUp(self):
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp()

        # Generate large JSON dataset (1000 items)
        self.large_json_data = {
            "items": []
        }

        for i in range(1000):
            self.large_json_data["items"].append({
                "id": i,
                "name": f"Item {i}",
                "value": i * 10,
                "active": i % 2 == 0,
                "tags": [f"tag{j}" for j in range(1, 6)]
            })

        self.large_json_file = os.path.join(self.temp_dir, "large_data.json")
        with open(self.large_json_file, 'w') as f:
            json.dump(self.large_json_data, f)

        # Generate large CSV dataset (1000 rows)
        self.large_csv_file = os.path.join(self.temp_dir, "large_data.csv")
        with open(self.large_csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "value", "active", "tag"])

            for i in range(1000):
                writer.writerow([
                    i,
                    f"Item {i}",
                    i * 10,
                    "true" if i % 2 == 0 else "false",
                    f"tag{i % 5 + 1}"
                ])

    def tearDown(self):
        # Clean up temp directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_json_adapter_performance(self):
        """Test JSONAdapter performance with large dataset"""
        adapter = JSONAdapter({"indent": None})  # Disable indentation for speed

        import time
        start_time = time.time()

        # Parse the file
        adapter.parse_file(self.large_json_file)
        data = adapter.execute()

        # Modify the data
        for item in data["items"]:
            item["processed"] = True

        # Convert back to JSON
        adapter.from_dict(data)
        json_str = adapter.execute()

        end_time = time.time()
        elapsed = end_time - start_time

        # Basic validation
        self.assertEqual(len(data["items"]), 1000)
        self.assertTrue("processed" in data["items"][0])

        print(f"JSON Adapter processing time: {elapsed:.2f} seconds")

    def test_csv_adapter_performance(self):
        """Test CSVAdapter performance with large dataset"""
        adapter = CSVAdapter({"delimiter": ","})

        import time
        start_time = time.time()

        # Parse the file
        adapter.parse_file(self.large_csv_file)
        data = adapter.execute()

        # Modify the data
        for row in data:
            row["processed"] = "true"

        # Export to new CSV
        output_file = os.path.join(self.temp_dir, "output_large.csv")
        adapter.from_list(data)
        csv_str = adapter.execute()

        with open(output_file, 'w') as f:
            f.write(csv_str)

        end_time = time.time()
        elapsed = end_time - start_time

        # Basic validation
        self.assertEqual(len(data), 1000)
        self.assertTrue("processed" in data[0])

        print(f"CSV Adapter processing time: {elapsed:.2f} seconds")


if __name__ == "__main__":
    unittest.main()