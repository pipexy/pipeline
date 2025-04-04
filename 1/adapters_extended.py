# adapters_extended.py
import subprocess
import os
import json
import tempfile
import requests
from typing import Dict, Any, List, Union


class ChainableAdapter:
    """Bazowa klasa dla adapterów, które można łączyć."""

    def __init__(self, name=None, previous=None):
        self.name = name
        self._params = {}
        self._previous = previous
        self._result = None

    def __getattr__(self, name):
        """Umożliwia dostęp do innych adapterów lub metod."""
        if name in ADAPTERS:
            # Zwraca instancję innego adaptera z referencją do aktualnego
            return ADAPTERS[name](previous=self)

        # Tworzy metodę dla danego parametru
        def method(value):
            self._params[name] = value
            return self

        return method

    def execute(self, input_data=None):
        """Wykonuje adapter oraz wszystkie poprzednie w łańcuchu."""
        if self._previous:
            # Wykonaj poprzedni adapter w łańcuchu
            input_data = self._previous.execute(input_data)

        # Wykonaj ten adapter
        return self._execute_self(input_data)

    def _execute_self(self, input_data=None):
        """Implementacja wykonania specyficzna dla konkretnego adaptera."""
        raise NotImplementedError("Subclasses must implement _execute_self()")

    def reset(self):
        """Resetuje parametry adaptera."""
        self._params = {}
        return self


class BashAdapter(ChainableAdapter):
    """Adapter wykonujący skrypty bash."""

    def _execute_self(self, input_data=None):
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


class HttpClientAdapter(ChainableAdapter):
    """Adapter wykonujący zapytania HTTP jako klient."""

    def _execute_self(self, input_data=None):
        url = self._params.get('url')
        method = self._params.get('method', 'GET').upper()
        headers = self._params.get('headers', {})

        if not url:
            raise ValueError("HTTP client adapter requires 'url' method")

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

        return response.text


class HttpServerAdapter(ChainableAdapter):
    """Adapter tworzący endpoint HTTP."""

    _app = None
    _routes = {}

    @classmethod
    def get_app(cls):
        """Zwraca lub tworzy aplikację Flask."""
        if cls._app is None:
            from flask import Flask
            cls._app = Flask(__name__)

            # Dodaj istniejące trasy
            for route_info in cls._routes.values():
                cls._add_route_to_app(route_info)

        return cls._app

    @classmethod
    def _add_route_to_app(cls, route_info):
        """Dodaje trasę do aplikacji Flask."""
        from flask import request, jsonify

        app = cls.get_app()
        path = route_info['path']
        methods = route_info['methods']
        handler = route_info['handler']

        @app.route(path, methods=methods)
        def route_handler(*args, **kwargs):
            # Przygotuj dane wejściowe
            input_data = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    input_data = request.json
                elif 'application/x-www-form-urlencoded' in content_type:
                    input_data = dict(request.form)
                else:
                    input_data = request.data.decode('utf-8')
            elif request.method == 'GET':
                input_data = dict(request.args)

            # Wywołaj handler
            result = handler(input_data)

            # Zwróć wynik
            if isinstance(result, (dict, list)):
                return jsonify(result)
            return result

    def _execute_self(self, input_data=None):
        path = self._params.get('path', '/')
        methods = self._params.get('methods', ['GET'])
        if isinstance(methods, str):
            methods = [methods]

        # Zapisz trasę do późniejszego dodania
        route_id = f"{','.join(methods)}:{path}"
        HttpServerAdapter._routes[route_id] = {
            'path': path,
            'methods': methods,
            'handler': lambda req_input: input_data
        }

        # Jeśli podano kod, wykonaj go aby uzyskać handler
        if 'code' in self._params:
            code = self._params['code']

            # Utwórz środowisko wykonawcze
            globals_dict = {
                'input_data': input_data,
                'params': self._params,
                'request_handler': None
            }

            # Wykonaj kod
            exec(code, globals_dict)

            # Pobierz handler
            handler = globals_dict.get('request_handler')
            if handler:
                HttpServerAdapter._routes[route_id]['handler'] = handler

        return {
            'server': 'http_server',
            'path': path,
            'methods': methods,
            'route_id': route_id
        }

    @classmethod
    def run_server(cls, host='127.0.0.1', port=5000):
        """Uruchamia serwer HTTP."""
        app = cls.get_app()
        app.run(host=host, port=port)


class PythonAdapter(ChainableAdapter):
    """Adapter wykonujący kod Python."""

    def _execute_self(self, input_data=None):
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


class DatabaseAdapter(ChainableAdapter):
    """Adapter do operacji bazodanowych."""

    def _execute_self(self, input_data=None):
        db_type = self._params.get('type', 'sqlite')
        connection_string = self._params.get('connection')
        query = self._params.get('query')

        if not query:
            raise ValueError("Database adapter requires 'query' method")

        if db_type == 'sqlite':
            import sqlite3

            # Obsługa SQLite
            conn = sqlite3.connect(connection_string or ':memory:')
            cursor = conn.cursor()

            # Wykonanie zapytania
            if isinstance(input_data, dict):
                cursor.execute(query, input_data)
            elif isinstance(input_data, list) and all(isinstance(item, dict) for item in input_data):
                cursor.executemany(query, input_data)
            else:
                cursor.execute(query)

            # Pobranie wyników
            if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                conn.commit()
                result = {'affected_rows': cursor.rowcount}

            conn.close()
            return result

        elif db_type == 'mysql':
            try:
                import mysql.connector

                # Obsługa MySQL
                conn = mysql.connector.connect(**json.loads(connection_string))
                cursor = conn.cursor(dictionary=True)

                # Wykonanie zapytania
                if isinstance(input_data, dict):
                    cursor.execute(query, input_data)
                elif isinstance(input_data, list) and all(isinstance(item, dict) for item in input_data):
                    cursor.executemany(query, input_data)
                else:
                    cursor.execute(query)

                # Pobranie wyników
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = {'affected_rows': cursor.rowcount}

                cursor.close()
                conn.close()
                return result

            except ImportError:
                raise ImportError("mysql-connector-python is required for MySQL connections")

        else:
            raise ValueError(f"Unsupported database type: {db_type}")


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
bash = BashAdapter('bash')
http_client = HttpClientAdapter('http_client')
http_server = HttpServerAdapter('http_server')
python = PythonAdapter('python')
database = DatabaseAdapter('database')
file = FileAdapter('file')

# Słownik dostępnych adapterów
ADAPTERS = {
    'bash': bash,
    'http_client': http_client,
    'http_server': http_server,
    'python': python,
    'database': database,
    'file': file
}