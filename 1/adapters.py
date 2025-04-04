# adapters.py
import subprocess
import os
import json
import tempfile
from typing import Dict, Any, List, Union


class BaseAdapter:
    """Bazowa klasa dla wszystkich adapterów."""

    def __init__(self, name):
        self.name = name
        self._params = {}

    def __getattr__(self, method_name):
        """Dynamicznie tworzy metody dla różnych parametrów."""

        def method(value):
            self._params[method_name] = value
            return self

        return method

    def execute(self, input_data=None):
        """Wykonuje adapter z ustawionymi parametrami."""
        raise NotImplementedError("Subclasses must implement execute()")

    def reset(self):
        """Resetuje parametry adaptera."""
        self._params = {}
        return self


class BashAdapter(BaseAdapter):
    """Adapter wykonujący skrypty bash."""

    def execute(self, input_data=None):
        # Zapisz dane wejściowe do pliku tymczasowego (jeśli istnieją)
        input_file = None
        if input_data:
            with tempfile.NamedTemporaryFile(delete=False, mode='w+') as f:
                if isinstance(input_data, dict) or isinstance(input_data, list):
                    json.dump(input_data, f)
                else:
                    f.write(str(input_data))
                input_file = f.name

        # Sprawdź czy podano komendę
        command = self._params.get('command')
        if not command:
            raise ValueError("Bash adapter requires 'command' method")

        # Zastąp placeholder $INPUT ścieżką do pliku wejściowego
        if input_file:
            command = command.replace('$INPUT', input_file)

        # Wykonaj komendę
        env = os.environ.copy()
        env.update(self._params.get('env', {}))

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            env=env
        )

        # Usuń plik tymczasowy jeśli był utworzony
        if input_file and os.path.exists(input_file):
            os.unlink(input_file)

        # Sprawdź wynik
        if result.returncode != 0 and not self._params.get('ignore_errors', False):
            raise RuntimeError(f"Bash command failed: {result.stderr}")

        # Zwróć wynik
        output = result.stdout.strip()

        # Automatycznie parsuj JSON jeśli wygląda jak JSON
        if output.startswith('{') or output.startswith('['):
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                pass

        return output


class PHPAdapter(BaseAdapter):
    """Adapter wykonujący kod PHP."""

    def execute(self, input_data=None):
        # Zapisz dane wejściowe do pliku tymczasowego (jeśli istnieją)
        input_file = None
        if input_data:
            with tempfile.NamedTemporaryFile(delete=False, mode='w+') as f:
                if isinstance(input_data, dict) or isinstance(input_data, list):
                    json.dump(input_data, f)
                else:
                    f.write(str(input_data))
                input_file = f.name

        # Zbuduj kod PHP
        code = self._params.get('code')
        file = self._params.get('file')

        if not code and not file:
            raise ValueError("PHP adapter requires 'code' or 'file' method")

        # Utworzenie tymczasowego pliku PHP jeśli podano kod bezpośrednio
        code_file = None
        if code:
            with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.php') as f:
                # Dodaj obsługę danych wejściowych
                if input_file:
                    input_var = (
                        f"<?php\n"
                        f"$input = json_decode(file_get_contents('{input_file}'), true);\n"
                        f"if (json_last_error() !== JSON_ERROR_NONE) {{\n"
                        f"    $input = file_get_contents('{input_file}');\n"
                        f"}}\n\n"
                    )
                    f.write(input_var)
                else:
                    f.write("<?php\n$input = null;\n\n")

                # Dodaj właściwy kod
                f.write(code)
                code_file = f.name

        # Wybuduj komendę PHP
        command = ['php']
        if code_file:
            command.append(code_file)
        elif file:
            command.append(file)
            # Przekaż dane wejściowe jako argument
            if input_file:
                command.append(input_file)

        # Wykonaj komendę PHP
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        # Usuń pliki tymczasowe
        if input_file and os.path.exists(input_file):
            os.unlink(input_file)
        if code_file and os.path.exists(code_file):
            os.unlink(code_file)

        # Sprawdź wynik
        if result.returncode != 0 and not self._params.get('ignore_errors', False):
            raise RuntimeError(f"PHP execution failed: {result.stderr}")

        # Zwróć wynik
        output = result.stdout.strip()

        # Automatycznie parsuj JSON jeśli wygląda jak JSON
        if output.startswith('{') or output.startswith('['):
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                pass

        return output


class NodeAdapter(BaseAdapter):
    """Adapter wykonujący kod Node.js."""

    def execute(self, input_data=None):
        # Zapisz dane wejściowe do pliku tymczasowego (jeśli istnieją)
        input_file = None
        if input_data:
            with tempfile.NamedTemporaryFile(delete=False, mode='w+') as f:
                if isinstance(input_data, dict) or isinstance(input_data, list):
                    json.dump(input_data, f)
                else:
                    f.write(str(input_data))
                input_file = f.name

        # Zbuduj kod Node.js
        code = self._params.get('code')
        file = self._params.get('file')

        if not code and not file:
            raise ValueError("Node adapter requires 'code' or 'file' method")

        # Utworzenie tymczasowego pliku JS jeśli podano kod bezpośrednio
        code_file = None
        if code:
            with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.js') as f:
                # Dodaj obsługę danych wejściowych
                if input_file:
                    input_var = (
                        f"const fs = require('fs');\n"
                        f"let input;\n"
                        f"try {{\n"
                        f"    input = JSON.parse(fs.readFileSync('{input_file}', 'utf8'));\n"
                        f"}} catch (e) {{\n"
                        f"    input = fs.readFileSync('{input_file}', 'utf8');\n"
                        f"}}\n\n"
                    )
                    f.write(input_var)
                else:
                    f.write("const input = null;\n\n")

                # Dodaj właściwy kod
                f.write(code)
                code_file = f.name

        # Wybuduj komendę Node.js
        command = ['node']
        if code_file:
            command.append(code_file)
        elif file:
            command.append(file)
            # Przekaż dane wejściowe jako argument
            if input_file:
                command.append(input_file)

        # Wykonaj komendę Node.js
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        # Usuń pliki tymczasowe
        if input_file and os.path.exists(input_file):
            os.unlink(input_file)
        if code_file and os.path.exists(code_file):
            os.unlink(code_file)

        # Sprawdź wynik
        if result.returncode != 0 and not self._params.get('ignore_errors', False):
            raise RuntimeError(f"Node.js execution failed: {result.stderr}")

        # Zwróć wynik
        output = result.stdout.strip()

        # Automatycznie parsuj JSON jeśli wygląda jak JSON
        if output.startswith('{') or output.startswith('['):
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                pass

        return output


class HttpAdapter(BaseAdapter):
    """Adapter wykonujący zapytania HTTP."""

    def execute(self, input_data=None):
        import requests

        url = self._params.get('url')
        method = self._params.get('method', 'GET').upper()
        headers = self._params.get('headers', {})

        if not url:
            raise ValueError("HTTP adapter requires 'url' method")

        request_params = {
            'headers': headers,
            'timeout': self._params.get('timeout', 30)
        }

        # Dodaj dane w zależności od metody
        if method in ['POST', 'PUT', 'PATCH']:
            if isinstance(input_data, dict) or isinstance(input_data, list):
                if 'Content-Type' in headers and headers['Content-Type'] == 'application/x-www-form-urlencoded':
                    request_params['data'] = input_data
                else:
                    request_params['json'] = input_data
            elif input_data:
                request_params['data'] = input_data
        elif input_data and isinstance(input_data, dict):
            request_params['params'] = input_data

        # Wykonaj zapytanie
        response = requests.request(method, url, **request_params)

        # Sprawdź status odpowiedzi
        if not response.ok and not self._params.get('ignore_errors', False):
            raise RuntimeError(f"HTTP request failed: {response.status_code} {response.reason}")

        # Próba automatycznego parsowania odpowiedzi
        content_type = response.headers.get('Content-Type', '')
        if 'json' in content_type:
            return response.json()
        elif 'xml' in content_type:
            # Można dodać parsowanie XML
            pass

        return response.text


class PythonAdapter(BaseAdapter):
    """Adapter wykonujący kod Python."""

    def execute(self, input_data=None):
        code = self._params.get('code')
        func = self._params.get('function')

        if not code and not func:
            raise ValueError("Python adapter requires 'code' or 'function' method")

        # Jeśli podano funkcję
        if func:
            if not callable(func):
                raise ValueError("'function' parameter must be callable")
            return func(input_data, **self._params.get('args', {}))

        # Jeśli podano kod
        if code:
            # Utwórz środowisko wykonawcze
            globals_dict = {
                'input_data': input_data,
                'params': self._params,
                'result': None
            }

            # Wykonaj kod
            exec(code, globals_dict)

            # Zwróć wynik
            return globals_dict.get('result')

        return None


# Utworzenie instancji adapterów
bash = BashAdapter('bash')
php = PHPAdapter('php')
node = NodeAdapter('node')
http = HttpAdapter('http')
python = PythonAdapter('python')

# Słownik dostępnych adapterów
ADAPTERS = {
    'bash': bash,
    'php': php,
    'node': node,
    'http': http,
    'python': python
}