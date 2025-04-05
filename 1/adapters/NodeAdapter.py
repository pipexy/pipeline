#!/usr/bin/env python3
# NodeAdapter.py

from .BaseAdapter import BaseAdapter
import json
import os
import subprocess
import tempfile

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
