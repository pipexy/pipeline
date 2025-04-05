#!/usr/bin/env python3
# http_server_adapter.py

# Adapter serwera HTTP

from flask import Flask, request, jsonify
import subprocess
import tempfile
import requests
from typing import Dict, Any, List, Union
from .ChainableAdapter import ChainableAdapter

class HttpServerAdapter(ChainableAdapter):
    """Adapter tworzący endpoint HTTP."""

    _app = None
    _routes = {}

    @classmethod
    def get_app(cls):
        """Zwraca lub tworzy aplikację Flask."""
        if cls._app is None:
            cls._app = Flask(__name__)

            # Dodaj istniejące trasy
            for route_info in cls._routes.values():
                cls._add_route_to_app(route_info)

        return cls._app

    @classmethod
    def _add_route_to_app(cls, route_info):
        """Dodaje trasę do aplikacji Flask."""

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

    @classmethod
    def stop_server(cls):
        """Zatrzymuje serwer HTTP."""
        import signal
        import subprocess

