"""
RegexAdapter.py
"""
import re
import os
from .ChainableAdapter import ChainableAdapter


class RegexAdapter(ChainableAdapter):
    """Adapter for regex pattern matching and manipulation."""

    def __init__(self, params=None):
        super().__init__(params)
        self._pattern = None
        self._operation = None
        self._content = None
        self._flags = 0

    def pattern(self, regex_pattern, flags=0):
        """Set the regex pattern and optional flags."""
        self._pattern = regex_pattern
        self._flags = flags
        return self

    def match(self, text=None):
        """Match pattern at the beginning of the string."""
        self._operation = 'match'
        if text is not None:
            self._content = text
        return self

    def search(self, text=None):
        """Search for pattern anywhere in the string."""
        self._operation = 'search'
        if text is not None:
            self._content = text
        return self

    def findall(self, text=None):
        """Find all occurrences of the pattern."""
        self._operation = 'findall'
        if text is not None:
            self._content = text
        return self

    def replace(self, replacement, text=None):
        """Replace pattern occurrences with replacement."""
        self._operation = 'replace'
        self._params['replacement'] = replacement
        if text is not None:
            self._content = text
        return self

    def split(self, text=None, maxsplit=0):
        """Split string by pattern occurrences."""
        self._operation = 'split'
        self._params['maxsplit'] = maxsplit
        if text is not None:
            self._content = text
        return self

    def from_file(self, file_path):
        """Load text from a file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            self._content = f.read()
        return self

    def _execute_self(self, input_data=None):
        try:
            # Get content
            content = self._content
            if content is None:
                if isinstance(input_data, str):
                    content = input_data
                else:
                    content = str(input_data) if input_data is not None else ""

            # Check pattern
            if self._pattern is None:
                raise ValueError("Regex pattern must be set first")

            # Perform regex operation
            if self._operation == 'match':
                match = re.match(self._pattern, content, self._flags)
                if match:
                    result = {
                        'matched': match.group(0),
                        'groups': match.groups(),
                        'start': match.start(),
                        'end': match.end()
                    }
                    if match.groupdict():
                        result['named_groups'] = match.groupdict()
                    return result
                return None

            elif self._operation == 'search':
                match = re.search(self._pattern, content, self._flags)
                if match:
                    result = {
                        'matched': match.group(0),
                        'groups': match.groups(),
                        'start': match.start(),
                        'end': match.end()
                    }
                    if match.groupdict():
                        result['named_groups'] = match.groupdict()
                    return result
                return None

            elif self._operation == 'findall':
                return re.findall(self._pattern, content, self._flags)

            elif self._operation == 'replace':
                replacement = self._params.get('replacement', '')
                return re.sub(self._pattern, replacement, content, flags=self._flags)

            elif self._operation == 'split':
                maxsplit = self._params.get('maxsplit', 0)
                return re.split(self._pattern, content, maxsplit=maxsplit, flags=self._flags)

            else:
                # Default operation: compile pattern and return it
                return re.compile(self._pattern, self._flags)

        except Exception as e:
            raise RuntimeError(f"Regex operation failed: {str(e)}")

    def reset(self):
        """Reset adapter state."""
        self._pattern = None
        self._operation = None
        self._content = None
        self._flags = 0
        self._params = {}
        return self