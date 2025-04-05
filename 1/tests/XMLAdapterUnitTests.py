# tests/test_xml_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
import xml.etree.ElementTree as ET

# Import the adapter to test
sys.path.append('..')
from adapters.XMLAdapter import XMLAdapter


class XMLAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_dir = tempfile.mkdtemp()
        self.test_xml = """
        <root>
            <person id="1">
                <name>John Doe</name>
                <age>30</age>
            </person>
            <person id="2">
                <name>Jane Smith</name>
                <age>25</age>
            </person>
        </root>
        """

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of XMLAdapter"""
        adapter = XMLAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    def test_parse_string(self):
        """Test parsing XML from a string"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        result = adapter.execute()

        # Verify the XML was parsed
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ET.Element)
        self.assertEqual(result.tag, 'root')

        # Check children
        people = list(result.findall('person'))
        self.assertEqual(len(people), 2)
        self.assertEqual(people[0].get('id'), '1')
        self.assertEqual(people[0].find('name').text, 'John Doe')

    def test_parse_file(self):
        """Test parsing XML from a file"""
        # Create a test XML file
        test_file = os.path.join(self.test_dir, "test.xml")
        with open(test_file, 'w') as f:
            f.write(self.test_xml)

        adapter = XMLAdapter({})
        adapter.parse_file(test_file)
        result = adapter.execute()

        # Verify the XML was parsed
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ET.Element)
        self.assertEqual(result.tag, 'root')

        # Clean up
        os.remove(test_file)

    def test_xpath_query(self):
        """Test querying XML with XPath"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.xpath("//person[@id='2']/name")
        result = adapter.execute()

        # Verify the query result
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, 'Jane Smith')

    def test_find_elements(self):
        """Test finding elements in XML"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.find_elements("person")
        result = adapter.execute()

        # Verify found elements
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get('id'), '1')
        self.assertEqual(result[1].get('id'), '2')

    def test_modify_elements(self):
        """Test modifying XML elements"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.find_elements("person")
        elements = adapter.execute()

        # Modify an element
        elements[0].find('age').text = '31'

        # Test that the modification took effect
        adapter.xpath("//person[@id='1']/age")
        result = adapter.execute()
        self.assertEqual(result[0].text, '31')

    def test_to_string(self):
        """Test converting XML to string"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.to_string()
        result = adapter.execute()

        # Verify it's a string representation of the XML
        self.assertIsInstance(result, str)
        self.assertTrue("<root>" in result)
        self.assertTrue("<person id=\"1\">" in result)
        self.assertTrue("<name>John Doe</name>" in result)

    def test_create_element(self):
        """Test creating a new XML element"""
        adapter = XMLAdapter({})
        adapter.create_element("user", {"id": "3"})
        root = adapter.execute()

        # Add some child elements
        name = ET.SubElement(root, "name")
        name.text = "Bob Johnson"

        age = ET.SubElement(root, "age")
        age.text = "40"

        # Verify the created element
        self.assertIsNotNone(root)
        self.assertEqual(root.tag, 'user')
        self.assertEqual(root.get('id'), '3')
        self.assertEqual(root.find('name').text, 'Bob Johnson')
        self.assertEqual(root.find('age').text, '40')

    def test_error_handling(self):
        """Test handling XML parsing errors"""
        # Invalid XML
        invalid_xml = "<root><unclosed>"

        adapter = XMLAdapter({})
        adapter.parse_string(invalid_xml)

        # Should raise an exception
        with self.assertRaises(Exception):
            adapter.execute()


if __name__ == "__main__":
    unittest.main()