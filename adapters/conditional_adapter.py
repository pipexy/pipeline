# Adapter dla warunków
"""
conditional_adapter.py
"""

# conditional_adapter.py
from adapters import ChainableAdapter


class ConditionalAdapter(ChainableAdapter):
    """Adapter do warunkowego wykonywania operacji."""

    def _execute_self(self, input_data=None):
        condition = self._params.get('condition')
        if_true = self._params.get('if_true')
        if_false = self._params.get('if_false')

        # Sprawdź, czy podano warunek
        if not condition:
            raise ValueError("Conditional adapter requires 'condition' parameter")

        # Sprawdź warunek
        result = False

        if callable(condition):
            # Jeśli to funkcja, wywołaj ją
            result = condition(input_data)
        elif isinstance(condition, str):
            # Jeśli to kod Pythona, wykonaj go
            global_vars = {
                'input_data': input_data,
                'params': self._params,
                'result': False
            }
            exec(condition, global_vars)
            result = global_vars.get('result', False)
        else:
            # Jeśli to wartość, użyj jej bezpośrednio
            result = bool(condition)

        # Wykonaj odpowiednią ścieżkę
        if result and if_true:
            if callable(if_true):
                return if_true(input_data)
            else:
                return if_true
        elif not result and if_false:
            if callable(if_false):
                return if_false(input_data)
            else:
                return if_false

        # Jeśli nie podano odpowiedniej ścieżki, zwróć dane wejściowe
        return input_data


# Dodaj adapter do dostępnych adapterów
conditional = ConditionalAdapter('conditional')
ADAPTERS['conditional'] = conditional