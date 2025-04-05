#!/usr/bin/env python3
# BashAdapter.py

from .BaseAdapter import BaseAdapter
import subprocess
import os
import json
import tempfile
from typing import Dict, Any, List, Union

class BashAdapter(BaseAdapter):
    """Adapter wykonujący skrypty bash."""

    def __init__(self, params: Dict[str, Any]):
        """Inicjalizacja adaptera."""
        super().__init__(params)

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
