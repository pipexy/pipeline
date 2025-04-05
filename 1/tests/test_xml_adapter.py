# tests/test_xml_adapter.py
import unittest
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

        # Create a test XML content
        self.test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <users>
            <user id="1">
                <name>John Doe</name>
                <email>john@example.com</email>
                <address>
                    <street>123 Main St</street>
                    <city>Anytown</city>
                </address>
                <roles>
                    <role>admin</role>
                    <role>user</role>
                </roles>
            </user>
            <user id="2">
                <name>Jane Smith</name>
                <email>jane@example.com</email>
                <address>
                    <street>456 Oak Ave</street>
                    <city>Somewhere</city>
                </address>
                <roles>
                    <role>user</role>
                </roles>
            </user>
        </users>
        """

        # Create a test XML file
        self.test_file = os.path.join(self.test_dir, "test.xml")
        with open(self.test_file, 'w') as f:
            f.write(self.test_xml)

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of XMLAdapter"""
        adapter = XMLAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    def test_parse_string(self):
        """Test parsing XML from string"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        result = adapter.execute()

        # Verify the XML was parsed
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'tag'))
        self.assertEqual(result.tag, "users")

    def test_parse_file(self):
        """Test parsing XML from file"""
        adapter = XMLAdapter({})
        adapter.parse_file(self.test_file)
        result = adapter.execute()

        # Verify the XML was parsed
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'tag'))
        self.assertEqual(result.tag, "users")

    def test_query_xpath(self):
        """Test querying XML with XPath"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.xpath("//user[@id='2']/name")
        result = adapter.execute()

        # Verify the XPath query result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Jane Smith")

    def test_find_element(self):
        """Test finding a specific element"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.find("user", {"id": "1"})
        result = adapter.execute()

        # Verify the found element
        self.assertIsNotNone(result)
        self.assertEqual(result.get("id"), "1")

    def test_find_all_elements(self):
        """Test finding all elements matching criteria"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.find_all("user")
        result = adapter.execute()

        # Verify all matching elements were found
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get("id"), "1")
        self.assertEqual(result[1].get("id"), "2")

    def test_get_element_text(self):
        """Test getting text from an element"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.xpath("//user[@id='1']/email")
        elements = adapter.execute()

        adapter = XMLAdapter({})
        adapter.get_text(elements[0])
        result = adapter.execute()

        # Verify the text content
        self.assertEqual(result, "john@example.com")

    def test_get_element_attribute(self):
        """Test getting an attribute value"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.xpath("//user[1]")
        elements = adapter.execute()

        adapter = XMLAdapter({})
        adapter.get_attribute(elements[0], "id")
        result = adapter.execute()

        # Verify the attribute value
        self.assertEqual(result, "1")

    def test_modify_element(self):
        """Test modifying an XML element"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.xpath("//user[@id='1']/name")
        elements = adapter.execute()

        # Modify the name
        elements[0].text = "John Smith"

        # Get the updated name
        adapter = XMLAdapter({})
        adapter.get_text(elements[0])
        result = adapter.execute()

        # Verify the modification
        self.assertEqual(result, "John Smith")

    def test_create_element(self):
        """Test creating a new XML element"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        root = adapter.execute()

        # Create a new user element
        new_user = ET.SubElement(root, "user", {"id": "3"})
        ET.SubElement(new_user, "name").text = "Bob Johnson"
        ET.SubElement(new_user, "email").text = "bob@example.com"

        # Find all users now
        adapter = XMLAdapter({})
        adapter.find_all_in_element(root, "user")
        result = adapter.execute()

        # Verify the new element was added
        self.assertEqual(len(result), 3)
        self.assertEqual(result[2].get("id"), "3")

    def test_write_to_file(self):
        """Test writing XML to a file"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        root = adapter.execute()

        # Modify the XML
        name_elem = root.find(".//user[@id='1']/name")
        name_elem.text = "John Modified"

        # Write to file
        output_file = os.path.join(self.test_dir, "output.xml")
        adapter = XMLAdapter({})
        adapter.write_element(root, output_file)
        adapter.execute()

        # Verify file was written
        self.assertTrue(os.path.exists(output_file))

        # Read it back
        with open(output_file, 'r') as f:
            content = f.read()

        self.assertTrue("John Modified" in content)

        # Clean up
        os.remove(output_file)

    def test_count_elements(self):
        """Test counting XML elements"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.xpath("//role")
        elements = adapter.execute()

        # Count the role elements
        self.assertEqual(len(elements), 3)  # 2 roles for John, 1 for Jane

    def test_filter_elements(self):
        """Test filtering XML elements"""
        adapter = XMLAdapter({})
        adapter.parse_string(self.test_xml)
        adapter.find_all("user")
        users = adapter.execute()

        # Find users with admin role
        admin_users = []
        for user in users:
            roles = user.findall(".//role")
            if any(role.text == "admin" for role in roles):
                admin_users.append(user)

        # Verify filtering
        self.assertEqual(len(admin_users), 1)
        self.assertEqual(admin_users[0].get("id"), "1")


if __name__ == "__main__":
    unittest.main()