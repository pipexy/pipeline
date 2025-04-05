#!/usr/bin/env python3
# zpl_adapter.py

"""
Adapter for ZPL (Zebra Programming Language)

This module provides a specialized adapter for handling ZPL (Zebra Programming Language) label generation and rendering.

The ZplAdapter supports multiple rendering modes:
- Labelary API rendering (default)
- Internal rendering

Key Features:
- Supports dynamic ZPL code processing
- Configurable rendering parameters (DPI, label dimensions)
- Multiple rendering backends
- Error handling for invalid or missing ZPL code

Supported Rendering Modes:
1. 'labelary': Uses Labelary API for label preview and rendering
2. 'internal': Uses internal rendering mechanism

Example Usage:
    adapter = ZplAdapter()
    result = adapter.execute({'zpl': '^XA...^XZ', 'render_mode': 'labelary'})
"""
# Adapter do obsługi języka ZPL (Zebra Programming Language).

import tempfile
import os
import json
import requests
from .ChainableAdapter import ChainableAdapter


class ZplAdapter(ChainableAdapter):
    """Adapter do renderowania kodu ZPL."""

    def _execute_self(self, input_data=None):
        # Pobierz kod ZPL z danych wejściowych
        zpl_code = input_data
        if isinstance(input_data, dict) and 'zpl' in input_data:
            zpl_code = input_data['zpl']
        elif isinstance(input_data, dict) and 'code' in input_data:
            zpl_code = input_data['code']

        # Sprawdź czy mamy kod ZPL
        if not zpl_code:
            raise ValueError("No ZPL code provided")

        # Sprawdź tryb renderowania
        render_mode = self._params.get('render_mode', 'labelary')

        if render_mode == 'labelary':
            return self._render_with_labelary(zpl_code)
        elif render_mode == 'internal':
            return self._render_internally(zpl_code)
        else:
            raise ValueError(f"Unsupported render mode: {render_mode}")

    def _render_with_labelary(self, zpl_code):
        """Renderowanie ZPL przez Labelary API."""
        # Parametry renderowania
        dpi = self._params.get('dpi', 203)
        width = self._params.get('width', 4)
        height = self._params.get('height', 6)

        # URL API
        api_url = self._params.get('api_url', 'https://api.labelary.com/v1/printers')
        endpoint = f"{api_url}/{dpi}/labels/{width}x{height}/0/"

        try:
            # Wywołanie API
            response = requests.post(
                endpoint,
                headers={'Accept': 'application/pdf'} if self._params.get('format') == 'pdf' else {},
                data=zpl_code
            )

            # Sprawdź status odpowiedzi
            if not response.ok:
                raise RuntimeError(f"Labelary API error: {response.status_code} {response.reason}")

            # Opcjonalnie zapisz wynik do pliku
            output_path = self._params.get('output_path')
            if output_path:
                # Utwórz katalogi jeśli nie istnieją
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                # Zapisz plik
                with open(output_path, 'wb') as f:
                    f.write(response.content)

            # Zwróć wynik
            return {
                'rendered': True,
                'image_data': response.content,
                'content_type': response.headers.get('Content-Type'),
                'format': 'pdf' if 'pdf' in response.headers.get('Content-Type', '') else 'png',
                'output_path': output_path,
                'dimensions': {
                    'dpi': dpi,
                    'width': width,
                    'height': height
                }
            }

        except Exception as e:
            raise RuntimeError(f"Error rendering ZPL with Labelary: {e}")

    def _render_internally(self, zpl_code):
        """Wewnętrzne renderowanie ZPL."""
        try:
            # Tutaj użycie wewnętrznego renderera, jeśli dostępny
            from emulators.zpl import render_zpl

            # Parametry renderowania
            dpi = self._params.get('dpi', 203)
            width = self._params.get('width', 4)
            height = self._params.get('height', 6)

            # Renderowanie
            result = render_zpl(zpl_code, dpi=dpi, width=width, height=height)

            # Opcjonalnie zapisz wynik do pliku
            output_path = self._params.get('output_path')
            if output_path and 'image' in result:
                # Utwórz katalogi jeśli nie istnieją
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                # Zapisz plik
                with open(output_path, 'wb') as f:
                    result['image'].save(f, format=self._params.get('format', 'PNG'))

            return {
                'rendered': True,
                'image': result.get('image'),
                'format': self._params.get('format', 'png').lower(),
                'output_path': output_path,
                'dimensions': {
                    'dpi': dpi,
                    'width': width,
                    'height': height
                },
                'elements': result.get('elements', [])
            }

        except ImportError:
            raise RuntimeError("Internal ZPL renderer not available. Use 'labelary' mode instead.")
        except Exception as e:
            raise RuntimeError(f"Error rendering ZPL internally: {e}")

    def render_mode(self, mode):
        """Ustawia tryb renderowania."""
        self._params['render_mode'] = mode
        return self

    def dpi(self, dpi):
        """Ustawia rozdzielczość DPI."""
        self._params['dpi'] = dpi
        return self

    def dimensions(self, width, height):
        """Ustawia wymiary etykiety."""
        self._params['width'] = width
        self._params['height'] = height
        return self

    def output(self, file_path):
        """Ustawia ścieżkę wyjściową dla zapisania rezultatu."""
        self._params['output_path'] = file_path
        return self

    def format(self, format_type):
        """Ustawia format wyjściowy (np. pdf, png)."""
        self._params['format'] = format_type
        return self

    def api_url(self, url):
        """Ustawia niestandardowy URL API Labelary."""
        self._params['api_url'] = url
        return self

    def code(self, zpl_code):
        """Ustawia kod ZPL do renderowania."""
        self._params['code'] = zpl_code
        return self

    def reset(self):
        """Resetuje parametry adaptera."""
        self._params = {}
        return self