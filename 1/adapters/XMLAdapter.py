#!/usr/bin/env python3
# XMLAdapter.py

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import json
import tempfile
from .ChainableAdapter import ChainableAdapter


class XMLAdapter(ChainableAdapter):
    """Adapter for handling XML data."""

    def __init__(self, params=None):
        super().__init__(params)
        self._root = None
        self._tree = None
        self._operation = None
        self._path = None

    def parse_string(self, xml_string):
        """Parse XML from string."""
        self._operation = 'parse_string'
        self._params['xml_string'] = xml_string
        return self

    def parse_file(self, file_path):
        """Parse XML from file."""
        self._operation = 'parse_file'
        self._path = file_path
        return self

    def query(self, xpath):
        """Query XML with XPath."""
        self._operation = 'query'
        self._params['xpath'] = xpath
        return self

    def create(self, root_tag, attributes=None):
        """Create new XML document."""
        self._operation = 'create'
        self._params['root_tag'] = root_tag
        self._params['attributes'] = attributes or {}
        return self

    def to_string(self, pretty=True):
        """Convert XML to string."""
        self._operation = 'to_string'
        self._params['pretty'] = pretty
        return self

    def write_file(self, file_path):
        """Write XML to file."""
        self._operation = 'write_file'
        self._path = file_path
        return self

    def _execute_self(self, input_data=None):
        try:
            # Operations that populate self._tree and self._root
            if self._operation == 'parse_string':
                xml_str = self._params.get('xml_string')
                self._root = ET.fromstring(xml_str)
                self._tree = ET.ElementTree(self._root)
                return self._root

            elif self._operation == 'parse_file':
                if not os.path.exists(self._path):
                    raise FileNotFoundError(f"XML file not found: {self._path}")
                self._tree = ET.parse(self._path)
                self._root = self._tree.getroot()
                return self._root

            elif self._operation == 'create':
                root_tag = self._params.get('root_tag', 'root')
                attributes = self._params.get('attributes', {})
                self._root = ET.Element(root_tag, attributes)
                self._tree = ET.ElementTree(self._root)
                return self._root

            # Operations that use existing XML
            elif self._operation == 'query':
                if self._root is None:
                    if isinstance(input_data, ET.Element):
                        self._root = input_data
                        self._tree = ET.ElementTree(self._root)
                    else:
                        raise ValueError("No XML document to query")

                xpath = self._params.get('xpath')
                found = self._root.findall(xpath)
                return found

            elif self._operation == 'to_string':
                if self._root is None:
                    if isinstance(input_data, ET.Element):
                        self._root = input_data
                        self._tree = ET.ElementTree(self._root)
                    else:
                        raise ValueError("No XML document to convert")

                rough_string = ET.tostring(self._root, 'utf-8')

                if self._params.get('pretty', True):
                    parsed = minidom.parseString(rough_string)
                    return parsed.toprettyxml(indent="  ")
                else:
                    return rough_string.decode('utf-8')

            elif self._operation == 'write_file':
                if self._root is None:
                    if isinstance(input_data, ET.Element):
                        self._root = input_data
                        self._tree = ET.ElementTree(self._root)
                    else:
                        raise ValueError("No XML document to write")

                self._tree.write(self._path, encoding='utf-8', xml_declaration=True)
                return self._path

            # Default handling for direct input
            if input_data is not None:
                if isinstance(input_data, str):
                    if os.path.exists(input_data):
                        self._tree = ET.parse(input_data)
                    else:
                        self._root = ET.fromstring(input_data)
                        self._tree = ET.ElementTree(self._root)
                elif isinstance(input_data, ET.Element):
                    self._root = input_data
                    self._tree = ET.ElementTree(self._root)

                return self._root

            return self._root

        except Exception as e:
            raise RuntimeError(f"XML operation failed: {str(e)}")

    def reset(self):
        """Reset adapter state."""
        self._root = None
        self._tree = None
        self._operation = None
        self._path = None
        self._params = {}
        return self