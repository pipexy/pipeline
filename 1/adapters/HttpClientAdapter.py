#!/usr/bin/env python3
# HttpClientAdapter.py

from .BaseAdapter import BaseAdapter
import json
import os
import subprocess
import tempfile
import requests


class HttpClientAdapter(BaseAdapter):
    """Adapter wykonujący zapytania HTTP."""


    def execute(self, input_data=None):

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
