# Adapter dla języka EPCOS
"""
epcos_adapter.py
"""

"""
Adapter do obsługi języka EPCOS.
"""

import os
import tempfile
from .base import BaseAdapter


class EpcosAdapter(BaseAdapter):
    """Adapter do przetwarzania i renderowania języka EPCOS."""

    def _execute_self(self, input_data=None):
        # Pobierz dane EPCOS
        epcos_data = input_data
        if isinstance(input_data, dict) and 'data' in input_data:
            epcos_data = input_data['data']
        elif isinstance(input_data, dict) and 'commands' in input_data:
            epcos_data = input_data['commands']

        # Sprawdź czy mamy dane
        if epcos_data is None:
            raise ValueError("No EPCOS data provided")

        # Konwersja do oczekiwanego formatu
        if isinstance(epcos_data, bytes):
            epcos_data = epcos_data.decode('latin-1')

        # Przetwarzanie
        try:
            # Próba użycia wewnętrznego modułu epcos
            from emulators.epcos import parse_epcos

            # Parametry przetwarzania
            dpi = self._params.get('dpi', 300)
            width = self._params.get('width', 210)  # szerokość w mm (A4)
            height = self._params.get('height', 297)  # wysokość w mm (A4)

            # Przetwarzanie
            result = parse_epcos(epcos_data, width=width, height=height, dpi=dpi)

            # Opcjonalnie zapisz wynik
            output_path = self._params.get('output_path')
            if output_path and 'image' in result:
                # Utwórz katalogi jeśli nie istnieją
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                # Zapisz plik
                result['image'].save(output_path, format=self._params.get('format', 'PNG'))

            # Zwróć wynik
            return {
                'processed': True,
                'image': result.get('image'),
                'output_path': output_path,
                'commands': result.get('commands', []),
                'dimensions': {
                    'dpi': dpi,
                    'width': width,
                    'height': height
                }
            }

        except ImportError:
            # Fallback - prosta emulacja EPCOS
            try:
                # Stwórz pustą kartkę
                from PIL import Image, ImageDraw, ImageFont

                # Konwersja mm na piksele
                dpi = self._params.get('dpi', 300)
                width_mm = self._params.get('width', 210)  # A4
                height_mm = self._params.get('height', 297)  # A4

                width_px = int(width_mm * dpi / 25.4)
                height_px = int(height_mm * dpi / 25.4)

                # Utwórz obraz
                image = Image.new('RGB', (width_px, height_px), color='white')
                draw = ImageDraw.Draw(image)

                # Prosta interpretacja komend
                lines = epcos_data.strip().split('\n')
                y_pos = 10  # Początkowa pozycja y

                try:
                    # Spróbuj znaleźć domyślną czcionkę
                    font = ImageFont.truetype("arial.ttf", 12)
                except:
                    # Fallback do czcionki domyślnej
                    font = ImageFont.load_default()

                for line in lines:
                    if line.startswith('TEXT'):
                        # Komenda tekstu: TEXT x y "treść"
                        parts = line.split(' ', 3)
                        if len(parts) >= 4:
                            x = int(parts[1])
                            y = int(parts[2])
                            text = parts[3].strip('"')
                            draw.text((x, y), text, fill='black', font=font)
                    elif line.startswith('LINE'):
                        # Komenda linii: LINE x1 y1 x2 y2
                        parts = line.split(' ')
                        if len(parts) >= 5:
                            x1 = int(parts[1])
                            y1 = int(parts[2])
                            x2 = int(parts[3])
                            y2 = int(parts[4])
                            draw.line([(x1, y1), (x2, y2)], fill='black', width=1)
                    elif line.startswith('RECT'):
                        # Komenda prostokąta: RECT x y width height
                        parts = line.split(' ')
                        if len(parts) >= 5:
                            x = int(parts[1])
                            y = int(parts[2])
                            w = int(parts[3])
                            h = int(parts[4])
                            draw.rectangle([(x, y), (x + w, y + h)], outline='black')
                    else:
                        # Nieznana komenda - dodaj jako tekst
                        draw.text((10, y_pos), line, fill='black', font=font)
                        y_pos += 15

                # Opcjonalnie zapisz wynik
                output_path = self._params.get('output_path')
                if output_path:
                    # Utwórz katalogi jeśli nie istnieją
                    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                    # Zapisz plik
                    image.save(output_path, format=self._params.get('format', 'PNG'))

                # Zwróć wynik
                return {
                    'processed': True,
                    'image': image,
                    'output_path': output_path,
                    'dimensions': {
                        'dpi': dpi,
                        'width': width_mm,
                        'height': height_mm
                    }
                }

            except Exception as e:
                raise RuntimeError(f"Error emulating EPCOS: {e}")