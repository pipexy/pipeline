# Adapter operacji na plikach
"""
file_adapter.py
"""


class FileAdapter(ChainableAdapter):
    """Adapter do operacji na plikach."""

    def _execute_self(self, input_data=None):
        operation = self._params.get('operation', 'read')
        path = self._params.get('path')

        if not path:
            raise ValueError("File adapter requires 'path' method")

        if operation == 'read':
            mode = self._params.get('mode', 'r')
            encoding = self._params.get('encoding', 'utf-8') if 'b' not in mode else None

            with open(path, mode, encoding=encoding) as f:
                content = f.read()

            # Automatycznie parsuj JSON
            if path.endswith('.json') and 'b' not in mode:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    pass

            return content

        elif operation == 'write':
            mode = self._params.get('mode', 'w')
            encoding = self._params.get('encoding', 'utf-8') if 'b' not in mode else None

            # Utwórz katalogi jeśli nie istnieją
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

            with open(path, mode, encoding=encoding) as f:
                if isinstance(input_data, (dict, list)) and 'b' not in mode:
                    json.dump(input_data, f, indent=2)
                else:
                    f.write(input_data)

            return {'success': True, 'path': path}

        else:
            raise ValueError(f"Unsupported file operation: {operation}")



# Tworzenie i rejestracja adapterów
file = FileAdapter('file')

# Słownik dostępnych adapterów
ADAPTERS = {
    'file': file
}