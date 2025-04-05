#!/usr/bin/env python3
# PHPAdapter.py

from .BaseAdapter import BaseAdapter
import json
import os
import subprocess
import tempfile


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