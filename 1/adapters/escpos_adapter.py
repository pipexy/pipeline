# Adapter dla języka ESC/POS
"""
escpos_adapter.py
"""

"""
Adapter do obsługi języka ESC/POS (dla drukarek termicznych).
"""

import tempfile
import os
import json
from .base import BaseAdapter


class EscPosAdapter(BaseAdapter):
    """Adapter do interpretacji i renderowania komend ESC/POS."""

    def _execute_self(self, input_data=None):
        # Pobierz dane ESC/POS
        escpos_data = input_data
        if isinstance(input_data, dict) and 'data' in input_data:
            escpos_data = input_data['data']
        elif isinstance(input_data, dict) and 'commands' in input_data:
            escpos_data = input_data['commands']

        # Sprawdź czy mamy dane
        if escpos_data is None:
            raise ValueError("No ESC/POS data provided")

        # Konwersja danych do binarnych jeśli potrzeba
        if isinstance(escpos_data, str):
            escpos_data = escpos_data.encode('latin-1')

        # Renderowanie
        try:
            from emulators.escpos import parse_escpos

            # Parametry renderowania
            width = self._params.get('width', 80)  # szerokość w mm
            dpi = self._params.get('dpi', 203)

            # Parsowanie komend
            result = parse_escpos(escpos_data, width=width, dpi=dpi)

            # Opcjonalnie zapisz wynik do pliku
            output_path = self._params.get('output_path')
            if output_path and 'image' in result:
                # Utwórz katalogi jeśli nie istnieją
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                # Zapisz plik
                result['image'].save(output_path, format=self._params.get('format', 'PNG'))

            return {
                'parsed': True,
                'image': result.get('image'),
                'text': result.get('text', ''),
                'width_px': result.get('width_px'),
                'height_px': result.get('height_px'),
                'output_path': output_path,
                'commands': result.get('commands', [])
            }

        except ImportError:
            # Próba użycia zewnętrznej biblioteki python-escpos
            try:
                from escpos.parser import Parser
                from escpos.printer import Dummy
                import io
                from PIL import Image

                # Utwórz wirtualną drukarkę
                dummy_printer = Dummy()

                # Parsuj komendy
                parser = Parser(dummy_printer)
                parser.feed(escpos_data)

                # Pobierz wynik
                output = dummy_printer.output

                # Opcjonalnie zapisz
                if output_path:
                    # Utwórz katalogi jeśli nie istnieją
                    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                    output.save(output_path)

                # Zwróć wynik
                return {
                    'parsed': True,
                    'image': output,
                    'output_path': output_path,
                    'width_px': output.width,
                    'height_px': output.height
                }

            except ImportError:
                raise RuntimeError("ESC/POS parser not available. Install 'python-escpos' package.")
            except Exception as e:
                raise RuntimeError(f"Error parsing ESC/POS: {e}")