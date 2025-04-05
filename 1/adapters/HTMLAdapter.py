"""
HTMLAdapter.py
"""
import os
from bs4 import BeautifulSoup
from .ChainableAdapter import ChainableAdapter


class HTMLAdapter(ChainableAdapter):
    """Adapter for parsing and manipulating HTML."""

    def __init__(self, params=None):
        super().__init__(params)
        self._soup = None
        self._operation = None
        self._path = None

    def parse_string(self, html_string):
        """Parse HTML from string."""
        self._operation = 'parse_string'
        self._params['html_string'] = html_string
        return self

    def parse_file(self, file_path):
        """Parse HTML from file."""
        self._operation = 'parse_file'
        self._path = file_path
        return self

    def select(self, css_selector):
        """Select elements using CSS selector."""
        self._operation = 'select'
        self._params['selector'] = css_selector
        return self

    def find(self, tag=None, attrs=None, text=None):
        """Find elements by tag, attributes or text."""
        self._operation = 'find'
        self._params['tag'] = tag
        self._params['attrs'] = attrs or {}
        self._params['text'] = text
        return self

    def extract_links(self):
        """Extract all links from HTML."""
        self._operation = 'extract_links'
        return self

    def extract_text(self):
        """Extract all text from HTML."""
        self._operation = 'extract_text'
        return self

    def to_string(self, pretty=True):
        """Convert HTML to string."""
        self._operation = 'to_string'
        self._params['pretty'] = pretty
        return self

    def write_file(self, file_path):
        """Write HTML to file."""
        self._operation = 'write_file'
        self._path = file_path
        return self

    def _execute_self(self, input_data=None):
        try:
            # Operations that populate self._soup
            if self._operation == 'parse_string':
                html_str = self._params.get('html_string')
                self._soup = BeautifulSoup(html_str, 'html.parser')
                return self._soup

            elif self._operation == 'parse_file':
                if not os.path.exists(self._path):
                    raise FileNotFoundError(f"HTML file not found: {self._path}")
                with open(self._path, 'r', encoding='utf-8') as f:
                    self._soup = BeautifulSoup(f, 'html.parser')
                return self._soup

            # Operations that use existing HTML
            elif self._operation == 'select':
                if self._soup is None:
                    if input_data is not None:
                        if isinstance(input_data, str):
                            self._soup = BeautifulSoup(input_data, 'html.parser')
                        else:
                            self._soup = input_data
                    else:
                        raise ValueError("No HTML to select from")

                selector = self._params.get('selector')
                return self._soup.select(selector)

            elif self._operation == 'find':
                if self._soup is None:
                    if input_data is not None:
                        if isinstance(input_data, str):
                            self._soup = BeautifulSoup(input_data, 'html.parser')
                        else:
                            self._soup = input_data
                    else:
                        raise ValueError("No HTML to find in")

                tag = self._params.get('tag')
                attrs = self._params.get('attrs', {})
                text = self._params.get('text')
                return self._soup.find_all(tag, attrs=attrs, text=text)

            elif self._operation == 'extract_links':
                if self._soup is None:
                    if input_data is not None:
                        if isinstance(input_data, str):
                            self._soup = BeautifulSoup(input_data, 'html.parser')
                        else:
                            self._soup = input_data
                    else:
                        raise ValueError("No HTML to extract links from")

                links = []
                for link in self._soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        links.append({
                            'text': link.text.strip(),
                            'href': href
                        })
                return links

            elif self._operation == 'extract_text':
                if self._soup is None:
                    if input_data is not None:
                        if isinstance(input_data, str):
                            self._soup = BeautifulSoup(input_data, 'html.parser')
                        else:
                            self._soup = input_data
                    else:
                        raise ValueError("No HTML to extract text from")

                return self._soup.get_text(separator=' ', strip=True)

            elif self._operation == 'to_string':
                if self._soup is None:
                    if input_data is not None:
                        if isinstance(input_data, str):
                            self._soup = BeautifulSoup(input_data, 'html.parser')
                        else:
                            self._soup = input_data
                    else:
                        raise ValueError("No HTML to convert")

                if self._params.get('pretty', True):
                    return self._soup.prettify()
                else:
                    return str(self._soup)

            elif self._operation == 'write_file':
                if self._soup is None:
                    if input_data is not None:
                        if isinstance(input_data, str):
                            self._soup = BeautifulSoup(input_data, 'html.parser')
                        else:
                            self._soup = input_data
                    else:
                        raise ValueError("No HTML to write")

                with open(self._path, 'w', encoding='utf-8') as f:
                    if self._params.get('pretty', True):
                        f.write(self._soup.prettify())
                    else:
                        f.write(str(self._soup))
                return self._path

            # Default handling for direct input
            if input_data is not None:
                if isinstance(input_data, str):
                    if os.path.exists(input_data):
                        with open(input_data, 'r', encoding='utf-8') as f:
                            self._soup = BeautifulSoup(f, 'html.parser')
                    else:
                        self._soup = BeautifulSoup(input_data, 'html.parser')
                else:
                    self._soup = input_data

                return self._soup

            return self._soup

        except Exception as e:
            raise RuntimeError(f"HTML operation failed: {str(e)}")

    def reset(self):
        """Reset adapter state."""
        self._soup = None
        self._operation = None
        self._path = None
        self._params = {}
        return self