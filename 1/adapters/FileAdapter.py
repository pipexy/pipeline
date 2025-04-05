"""
FileAdapter.py - Adapter for file system operations

This adapter provides functionality to work with files and directories:
- Reading and writing files
- Checking file existence
- File and directory manipulation
- Handling various file formats
"""

import os
import shutil
import json
import pickle
import tempfile
from pathlib import Path
from .ChainableAdapter import ChainableAdapter

class FileAdapter(ChainableAdapter):
    """Adapter for handling file system operations in a chainable way."""

    def __init__(self, params=None):
        super().__init__(params)
        self._operation = None
        self._file_path = None
        self._content = None

    def read(self, file_path=None):
        """Read content from a file."""
        self._operation = 'read'
        if file_path:
            self._params['file_path'] = file_path
        return self

    def write(self, file_path=None, content=None):
        """Write content to a file."""
        self._operation = 'write'
        if file_path:
            self._params['file_path'] = file_path
        if content is not None:
            self._params['content'] = content
        return self

    def append(self, file_path=None, content=None):
        """Append content to a file."""
        self._operation = 'append'
        if file_path:
            self._params['file_path'] = file_path
        if content is not None:
            self._params['content'] = content
        return self

    def exists(self, file_path=None):
        """Check if a file exists."""
        self._operation = 'exists'
        if file_path:
            self._params['file_path'] = file_path
        return self

    def delete(self, file_path=None):
        """Delete a file or directory."""
        self._operation = 'delete'
        if file_path:
            self._params['file_path'] = file_path
        return self

    def copy(self, source=None, destination=None):
        """Copy a file or directory."""
        self._operation = 'copy'
        if source:
            self._params['source'] = source
        if destination:
            self._params['destination'] = destination
        return self

    def move(self, source=None, destination=None):
        """Move a file or directory."""
        self._operation = 'move'
        if source:
            self._params['source'] = source
        if destination:
            self._params['destination'] = destination
        return self

    def list_dir(self, directory=None):
        """List contents of a directory."""
        self._operation = 'list_dir'
        if directory:
            self._params['directory'] = directory
        return self

    def make_dir(self, directory=None, exist_ok=True):
        """Create a directory."""
        self._operation = 'make_dir'
        if directory:
            self._params['directory'] = directory
        self._params['exist_ok'] = exist_ok
        return self

    def temp_file(self, suffix=None, prefix=None, dir=None):
        """Create a temporary file."""
        self._operation = 'temp_file'
        if suffix:
            self._params['suffix'] = suffix
        if prefix:
            self._params['prefix'] = prefix
        if dir:
            self._params['dir'] = dir
        return self

    def _execute_self(self, input_data=None):
        try:
            # Get file path from params or input
            file_path = self._params.get('file_path')
            if not file_path and isinstance(input_data, str) and self._operation not in ['list_dir', 'make_dir']:
                if os.path.exists(input_data) or self._operation == 'write':
                    file_path = input_data

            content = self._params.get('content', input_data)

            # Handle different operations
            if self._operation == 'read':
                if not file_path:
                    raise ValueError("No file path provided for read operation")

                mode = 'r'
                # Auto-detect binary mode if needed
                if self._params.get('mode') == 'binary' or self._params.get('binary'):
                    mode = 'rb'

                with open(file_path, mode) as f:
                    content = f.read()

                # Auto-detect and parse formats
                if self._params.get('parse', True) and not mode == 'rb':
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext == '.json':
                        content = json.loads(content)
                    elif ext == '.pkl' or ext == '.pickle':
                        with open(file_path, 'rb') as f:
                            content = pickle.load(f)

                return content

            elif self._operation == 'write':
                if not file_path:
                    raise ValueError("No file path provided for write operation")

                # Create directory if it doesn't exist
                directory = os.path.dirname(file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)

                # Determine mode and format
                if isinstance(content, (dict, list)) and (self._params.get('format') == 'json' or
                                                         file_path.endswith('.json')):
                    with open(file_path, 'w') as f:
                        json.dump(content, f, indent=self._params.get('indent', 2))
                elif self._params.get('format') == 'pickle' or file_path.endswith(('.pkl', '.pickle')):
                    with open(file_path, 'wb') as f:
                        pickle.dump(content, f)
                elif isinstance(content, bytes):
                    with open(file_path, 'wb') as f:
                        f.write(content)
                else:
                    with open(file_path, 'w') as f:
                        f.write(str(content))

                return {"status": "success", "file": file_path}

            elif self._operation == 'append':
                if not file_path:
                    raise ValueError("No file path provided for append operation")

                # Create directory if it doesn't exist
                directory = os.path.dirname(file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)

                # Append mode depends on content type
                if isinstance(content, bytes):
                    with open(file_path, 'ab') as f:
                        f.write(content)
                else:
                    with open(file_path, 'a') as f:
                        f.write(str(content))

                return {"status": "success", "file": file_path}

            elif self._operation == 'exists':
                if not file_path:
                    raise ValueError("No file path provided for exists operation")
                return os.path.exists(file_path)

            elif self._operation == 'delete':
                if not file_path:
                    raise ValueError("No file path provided for delete operation")

                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                elif os.path.exists(file_path):
                    os.remove(file_path)

                return {"status": "success", "deleted": file_path}

            elif self._operation == 'copy':
                source = self._params.get('source')
                destination = self._params.get('destination')

                if not source or not destination:
                    raise ValueError("Both source and destination are required for copy operation")

                if os.path.isdir(source):
                    shutil.copytree(source, destination)
                else:
                    # Create destination directory if needed
                    dest_dir = os.path.dirname(destination)
                    if dest_dir and not os.path.exists(dest_dir):
                        os.makedirs(dest_dir, exist_ok=True)
                    shutil.copy2(source, destination)

                return {"status": "success", "source": source, "destination": destination}

            elif self._operation == 'move':
                source = self._params.get('source')
                destination = self._params.get('destination')

                if not source or not destination:
                    raise ValueError("Both source and destination are required for move operation")

                # Create destination directory if needed
                dest_dir = os.path.dirname(destination)
                if dest_dir and not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)

                shutil.move(source, destination)
                return {"status": "success", "source": source, "destination": destination}

            elif self._operation == 'list_dir':
                directory = self._params.get('directory', '.')

                if not os.path.exists(directory):
                    raise ValueError(f"Directory does not exist: {directory}")

                files = os.listdir(directory)
                if self._params.get('full_paths', False):
                    files = [os.path.join(directory, f) for f in files]

                return files

            elif self._operation == 'make_dir':
                directory = self._params.get('directory')
                exist_ok = self._params.get('exist_ok', True)

                if not directory:
                    raise ValueError("No directory path provided")

                os.makedirs(directory, exist_ok=exist_ok)
                return {"status": "success", "directory": directory}

            elif self._operation == 'temp_file':
                suffix = self._params.get('suffix', '')
                prefix = self._params.get('prefix', 'tmp')
                dir = self._params.get('dir')

                with tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix,
                                                dir=dir, delete=False) as tmp:
                    temp_name = tmp.name
                    if content is not None:
                        if isinstance(content, bytes):
                            tmp.write(content)
                        else:
                            tmp.write(str(content).encode())

                return {"status": "success", "file": temp_name}

            # Default behavior if no operation specified
            if input_data is not None:
                if isinstance(input_data, str) and os.path.exists(input_data):
                    # Read file if input looks like a path
                    with open(input_data, 'r') as f:
                        return f.read()

            return input_data

        except Exception as e:
            raise RuntimeError(f"File operation failed: {str(e)}")

    def format(self, format_type):
        """Set output format for write operations."""
        self._params['format'] = format_type
        return self

    def binary(self, is_binary=True):
        """Set binary mode for file operations."""
        self._params['binary'] = is_binary
        return self

    def parse(self, should_parse=True):
        """Control automatic parsing of file contents."""
        self._params['parse'] = should_parse
        return self