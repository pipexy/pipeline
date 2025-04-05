# Klasa kontekstu wykonania
"""
context.py
"""

"""
Moduł definiujący kontekst wykonania dla pipeline'ów i workflow.
"""

import time
import os
import json
from datetime import datetime
import uuid


class ExecutionContext:
    """
    Kontekst wykonania przechowujący dane i stan podczas wykonywania pipeline'ów.
    """

    def __init__(self, input_data=None, env=None):
        """
        Inicjalizacja kontekstu wykonania.

        Args:
            input_data: Początkowe dane wejściowe
            env: Zmienne środowiskowe
        """
        self.input = input_data or {}
        self.results = {}
        self.errors = []
        self.start_time = time.time()
        self.metadata = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'env': env or {}
        }
        self.variables = {
            'timestamp': int(time.time()),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H-%M-%S')
        }

    def add_result(self, step_id, result):
        """Dodaje wynik kroku do kontekstu."""
        self.results[step_id] = result
        return self

    def add_error(self, step_id, error):
        """Dodaje błąd do kontekstu."""
        self.errors.append({
            'step_id': step_id,
            'error': str(error),
            'timestamp': time.time()
        })
        return self

    def get_duration(self):
        """Zwraca czas wykonania w sekundach."""
        return time.time() - self.start_time

    def get_result(self, step_id):
        """Pobiera wynik konkretnego kroku."""
        return self.results.get(step_id)

    def get_variable(self, name, default=None):
        """Pobiera zmienną z kontekstu."""
        return self.variables.get(name, default)

    def set_variable(self, name, value):
        """Ustawia zmienną w kontekście."""
        self.variables[name] = value
        return self

    def resolve_path(self, path):
        """Rozwiązuje ścieżkę do wartości w kontekście."""
        if not path or not isinstance(path, str):
            return path

        # Format: results.step_id.property
        parts = path.split('.')

        if parts[0] == 'results':
            # Ścieżka do wyniku kroku
            if len(parts) < 2:
                return self.results

            step_id = parts[1]
            if step_id not in self.results:
                return None

            value = self.results[step_id]

            # Zagnieżdżone właściwości
            for part in parts[2:]:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None

            return value

        elif parts[0] == 'variables':
            # Ścieżka do zmiennej
            if len(parts) < 2:
                return self.variables

            var_name = parts[1]
            return self.variables.get(var_name)

        elif parts[0] == 'input':
            # Ścieżka do danych wejściowych
            value = self.input

            # Zagnieżdżone właściwości
            for part in parts[1:]:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None

            return value

        return None

    def to_dict(self):
        """Konwertuje kontekst do słownika."""
        return {
            'input': self.input,
            'results': self.results,
            'errors': self.errors,
            'metadata': {
                **self.metadata,
                'duration': self.get_duration()
            },
            'variables': self.variables
        }

    def save_to_file(self, file_path):
        """Zapisuje kontekst do pliku JSON."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)