"""
MarkdownAdapter.py
"""
import os
import markdown
import re
from .ChainableAdapter import ChainableAdapter


class MarkdownAdapter(ChainableAdapter):
    """Adapter for working with Markdown content."""

    def __init__(self, params=None):
        super().__init__(params)
        self._content = None
        self._operation = None
        self._path = None

    def parse_file(self, file_path):
        """Read markdown from file."""
        self._operation = 'parse_file'
        self._path = file_path
        return self

    def parse_string(self, md_string):
        """Parse markdown from string."""
        self._operation = 'parse_string'
        self._params['md_string'] = md_string
        return self

    def to_html(self, extensions=None):
        """Convert markdown to HTML."""
        self._operation = 'to_html'
        self._params['extensions'] = extensions or []
        return self

    def extract_headers(self, level=None):
        """Extract headers from markdown."""
        self._operation = 'extract_headers'
        self._params['level'] = level
        return self

    def extract_code_blocks(self, language=None):
        """Extract code blocks from markdown."""
        self._operation = 'extract_code_blocks'
        self._params['language'] = language
        return self

    def extract_links(self):
        """Extract links from markdown."""
        self._operation = 'extract_links'
        return self

    def write_file(self, file_path):
        """Write markdown to file."""
        self._operation = 'write_file'
        self._path = file_path
        return self

    def _execute_self(self, input_data=None):
        try:
            # Operations that populate self._content
            if self._operation == 'parse_file':
                if not os.path.exists(self._path):
                    raise FileNotFoundError(f"Markdown file not found: {self._path}")
                with open(self._path, 'r', encoding='utf-8') as f:
                    self._content = f.read()
                return self._content

            elif self._operation == 'parse_string':
                self._content = self._params.get('md_string')
                return self._content

            # Operations that use existing Markdown
            elif self._operation == 'to_html':
                if self._content is None:
                    if input_data is not None:
                        self._content = input_data
                    else:
                        raise ValueError("No Markdown content to convert")

                extensions = self._params.get('extensions', [])
                return markdown.markdown(self._content, extensions=extensions)

            elif self._operation == 'extract_headers':
                if self._content is None:
                    if input_data is not None:
                        self._content = input_data
                    else:
                        raise ValueError("No Markdown content to extract headers from")

                level = self._params.get('level')
                if level:
                    pattern = rf'^#{{{level}}} (.+)$'
                else:
                    pattern = r'^(#{1,6}) (.+)$'

                headers = []
                for line in self._content.splitlines():
                    if level:
                        match = re.match(pattern, line)
                        if match:
                            headers.append({
                                'level': level,
                                'text': match.group(1).strip()
                            })
                    else:
                        match = re.match(pattern, line)
                        if match:
                            headers.append({
                                'level': len(match.group(1)),
                                'text': match.group(2).strip()
                            })

                return headers

            elif self._operation == 'extract_code_blocks':
                if self._content is None:
                    if input_data is not None:
                        self._content = input_data
                    else:
                        raise ValueError("No Markdown content to extract code blocks from")

                language = self._params.get('language')
                if language:
                    pattern = rf'```{language}\n(.*?)\n```'
                else:
                    pattern = r'```(\w*)\n(.*?)\n```'

                code_blocks = []
                if language:
                    matches = re.findall(pattern, self._content, re.DOTALL)
                    for match in matches:
                        code_blocks.append({
                            'language': language,
                            'code': match.strip()
                        })
                else:
                    matches = re.findall(pattern, self._content, re.DOTALL)
                    for lang, code in matches:
                        code_blocks.append({
                            'language': lang or 'text',
                            'code': code.strip()
                        })

                return code_blocks

            elif self._operation == 'extract_links':
                if self._content is None:
                    if input_data is not None:
                        self._content = input_data
                    else:
                        raise ValueError("No Markdown content to extract links from")

                # Find standard Markdown links: [text](url)
                links = []
                for match in re.findall(r'\[(.*?)\]\((.*?)\)', self._content):
                    links.append({
                        'text': match[0],
                        'url': match[1]
                    })

                return links

            elif self._operation == 'write_file':
                if self._content is None:
                    if input_data is not None:
                        self._content = input_data
                    else:
                        raise ValueError("No Markdown content to write")

                with open(self._path, 'w', encoding='utf-8') as f:
                    f.write(self._content)
                return self._path

            # Default handling for direct input
            if input_data is not None:
                if isinstance(input_data, str):
                    if os.path.exists(input_data):
                        with open(input_data, 'r', encoding='utf-8') as f:
                            self._content = f.read()
                    else:
                        self._content = input_data
                return self._content

            return self._content

        except Exception as e:
            raise RuntimeError(f"Markdown operation failed: {str(e)}")

    def reset(self):
        """Reset adapter state."""
        self._content = None
        self._operation = None
        self._path = None
        self._params = {}
        return self