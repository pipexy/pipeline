# Adapter dla języka PCL
"""
pcl_adapter.py
"""

"""
Adapter do obsługi języka PCL (Printer Command Language).
"""

import os
import tempfile
import subprocess
from .base import BaseAdapter


class PclAdapter(BaseAdapter):
    """Adapter do przetwarzania i renderowania języka PCL."""

    def _execute_self(self, input_data=None):
        # Pobierz dane PCL
        pcl_data = input_data
        if isinstance(input_data, dict) and 'data' in input_data:
            pcl_data = input_data['data']
        elif isinstance(input_data, dict) and 'commands' in input_data:
            pcl_data = input_data['commands']

        # Sprawdź czy mamy dane
        if pcl_data is None:
            raise ValueError("No PCL data provided")

        # Konwersja do binarnej formy jeśli potrzeba
        if isinstance(pcl_data, str):
            pcl_data = pcl_data.encode('latin-1')

        # Sprawdź tryb przetwarzania
        process_mode = self._params.get('mode', 'ghostscript')

        if process_mode == 'ghostscript':
            return self._process_with_ghostscript(pcl_data)
        elif process_mode == 'internal':
            return self._process_internally(pcl_data)
        else:
            raise ValueError(f"Unsupported PCL processing mode: {process_mode}")

    def _process_with_ghostscript(self, pcl_data):
        """Przetwarzanie PCL za pomocą Ghostscript."""
        try:
            # Parametry przetwarzania
            dpi = self._params.get('dpi', 300)
            format = self._params.get('format', 'png').lower()

            # Utwórz plik tymczasowy na wejście
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pcl', mode='wb') as temp_in:
                temp_in.write(pcl_data)
                temp_in_path = temp_in.name

            # Utwórz plik tymczasowy na wyjście
            temp_out_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{format}')
            temp_out_file.close()
            temp_out_path = temp_out_file.name

            # Przygotuj komendę Ghostscript
            gs_cmd = [
                'gs',
                '-dNOPAUSE',
                '-dBATCH',
                '-dSAFER',
                f'-r{dpi}',
                f'-sDEVICE={format}16m' if format == 'png' else f'-sDEVICE={format}',
                f'-sOutputFile={temp_out_path}',
                temp_in_path
            ]

            # Wykonaj komendę
            process = subprocess.run(
                gs_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            # Odczytaj wynik
            output_data = None
            with open(temp_out_path, 'rb') as f:
                output_data = f.read()

            # Opcjonalnie zapisz wynik
            output_path = self._params.get('output_path')
            if output_path:
                # Utwórz katalogi jeśli nie istnieją
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                # Zapisz plik
                with open(output_path, 'wb') as f:
                    f.write(output_data)

            # Usuń pliki tymczasowe
            try:
                os.unlink(temp_in_path)
                os.unlink(temp_out_path)
            except:
                pass

            # Zwróć wynik
            return {
                'processed': True,
                'image_data': output_data,
                'format': format,
                'output_path': output_path,
                'ghostscript_output': process.stdout.decode('utf-8') if process.stdout else None,
                'dimensions': {
                    'dpi': dpi
                }
            }

        except subprocess.CalledProcessError as e:
            # Błąd wykonania Ghostscript
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            raise RuntimeError(f"Ghostscript error processing PCL: {error_msg}")
        except Exception as e:
            raise RuntimeError(f"Error processing PCL with Ghostscript: {e}")

    def _process_internally(self, pcl_data):
        """Wewnętrzne przetwarzanie PCL."""
        try:
            # Próba użycia wewnętrznego modułu pcl
            from emulators.pcl import parse_pcl

            # Parametry przetwarzania
            dpi = self._params.get('dpi', 300)

            # Przetwarzanie
            result = parse_pcl(pcl_data, dpi=dpi)

            # Opcjonalnie zapisz wynik
            output_path = self._params.get('output_path')
            if output_path and 'image' in result:
                # Utwórz katalogi jeśli nie istnieją
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                # Zapisz plik
                result['image'].save(output_path)

            # Zwróć wynik
            return {
                'processed': True,
                'image': result.get('image'),
                'output_path': output_path,
                'commands': result.get('commands', []),
                'dimensions': {
                    'dpi': dpi,
                    'width': result.get('width'),
                    'height': result.get('height')
                }
            }

        except ImportError:
            raise RuntimeError("Internal PCL parser not available. Use 'ghostscript' mode instead.")
        except Exception as e:
            raise RuntimeError(f"Error processing PCL internally: {e}")