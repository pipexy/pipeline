# Silnik workflow ze wsparciem zależności
"""
workflow_engine.py
"""

# workflow_engine.py
import yaml
import json
import time
import os
import re
from adapters_extended import ADAPTERS
from dsl_parser import YamlDSLParser


class WorkflowEngine:
    """Silnik wykonujący workflow zdefiniowany w YAML."""

    def __init__(self):
        self.workflows = {}

    def load_workflow(self, yaml_path):
        """Ładuje workflow z pliku YAML."""
        try:
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)

            if 'workflow' not in config:
                raise ValueError(f"Invalid workflow file: {yaml_path}")

            workflow_id = os.path.splitext(os.path.basename(yaml_path))[0]
            self.workflows[workflow_id] = config['workflow']

            return workflow_id
        except Exception as e:
            raise ValueError(f"Error loading workflow: {e}")

    def execute_workflow(self, workflow_id, inputs=None):
        """Wykonuje workflow o podanym ID."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]

        # Kontekst wykonania
        context = {
            'inputs': self._process_inputs(workflow.get('inputs', []), inputs or {}),
            'steps': {},
            'outputs': {},
            'timestamp': int(time.time()),
            'workflow_id': workflow_id
        }

        # Zbuduj graf zależności
        dependency_graph = self._build_dependency_graph(workflow.get('steps', []))

        # Wykonanie kroków w odpowiedniej kolejności
        executed_steps = set()
        all_steps = set(step['id'] for step in workflow.get('steps', []))

        while executed_steps != all_steps:
            progress_made = False

            for step in workflow.get('steps', []):
                step_id = step['id']

                # Sprawdź czy krok został już wykonany
                if step_id in executed_steps:
                    continue

                # Sprawdź czy wszystkie zależności zostały wykonane
                dependencies = dependency_graph.get(step_id, [])
                if not all(dep in executed_steps for dep in dependencies):
                    continue

                # Sprawdź warunek
                condition = step.get('condition')
                if condition and not self._evaluate_condition(condition, context):
                    # Oznacz krok jako wykonany, ale pomijamy jego faktyczne wykonanie
                    executed_steps.add(step_id)
                    context['steps'][step_id] = {'skipped': True}
                    progress_made = True
                    continue

                # Wykonaj krok
                try:
                    result = self._execute_step(step, context)
                    context['steps'][step_id] = {'output': result, 'success': True}
                    executed_steps.add(step_id)
                    progress_made = True
                except Exception as e:
                    context['steps'][step_id] = {'error': str(e), 'success': False}
                    executed_steps.add(step_id)
                    progress_made = True

                    # Opcjonalnie, możemy przerwać całe wykonanie przy błędzie
                    if not workflow.get('continue_on_error', False):
                        raise RuntimeError(f"Step {step_id} failed: {e}")

            # Jeśli nie było postępu, a nie wszystkie kroki zostały wykonane,
            # mamy cykl zależności lub brakujące zależności
            if not progress_made and executed_steps != all_steps:
                remaining = all_steps - executed_steps
                raise ValueError(f"Cannot resolve dependencies for steps: {remaining}")

        # Przygotowanie wyników
        self._process_outputs(workflow.get('outputs', []), context)

        return context

    def _process_inputs(self, input_specs, provided_inputs):
        """Przetwarza dane wejściowe na podstawie specyfikacji."""
        result = {}

        for spec in input_specs:
            name = spec['name']

            # Jeśli wartość została dostarczona
            if name in provided_inputs:
                result[name] = provided_inputs[name]
            # W przeciwnym razie użyj wartości domyślnej
            elif 'default' in spec:
                result[name] = spec['default']
            # Jeśli wymagane pole nie zostało dostarczone
            elif spec.get('required', False):
                raise ValueError(f"Required input '{name}' not provided")

        return result

    def _build_dependency_graph(self, steps):
        """Buduje graf zależności dla kroków workflow."""
        graph = {}

        for step in steps:
            step_id = step['id']
            dependencies = step.get('depends_on', [])

            # Konwersja na listę jeśli to pojedynczy string
            if isinstance(dependencies, str):
                dependencies = [dependencies]

            graph[step_id] = dependencies

        # Sprawdź, czy nie ma cykli zależności
        visited = set()
        temp_visited = set()

        def check_cycles(node):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected involving step: {node}")

            if node in visited:
                return

            temp_visited.add(node)

            for neighbor in graph.get(node, []):
                check_cycles(neighbor)

            temp_visited.remove(node)
            visited.add(node)

        # Sprawdź każdy węzeł
        for node in graph:
            if node not in visited:
                check_cycles(node)

        return graph

    def _evaluate_condition(self, condition, context):
        """Ewaluuje warunek z interpolacją zmiennych."""
        # Jeśli warunek jest już wartością logiczną
        if isinstance(condition, bool):
            return condition

        # Interpoluj zmienne w warunku
        interpolated_condition = self._interpolate_string(condition, context)

        # Ewaluuj warunek
        try:
            # Bezpieczniejsza ewaluacja
            result = eval(interpolated_condition, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            raise ValueError(f"Error evaluating condition '{condition}': {e}")

    def _execute_step(self, step, context):
        """Wykonuje pojedynczy krok workflow."""
        adapter_name = step.get('adapter')
        methods = step.get('methods', [])

        if not adapter_name or adapter_name not in ADAPTERS:
            raise ValueError(f"Unknown adapter: {adapter_name}")

        # Pobierz adapter
        adapter = ADAPTERS[adapter_name]
        adapter.reset()

        # Przygotuj dane wejściowe
        input_data = self._resolve_input_data(step, context)

        # Zastosuj metody
        for method in methods:
            method_name = method.get('name')
            method_value = method.get('value')

            if not method_name:
                continue

            # Interpoluj zmienne w wartości metody
            if isinstance(method_value, str):
                method_value = self._interpolate_string(method_value, context)

            # Wywołaj metodę
            getattr(adapter, method_name)(method_value)

        # Wykonaj adapter
        return adapter.execute(input_data)

    def _resolve_input_data(self, step, context):
        """Rozwiązuje dane wejściowe dla kroku workflow."""
        # Domyślnie, użyj danych z poprzedniego kroku
        if 'input' not in step:
            # Znajdź poprzedni krok na podstawie zależności
            depends_on = step.get('depends_on', [])

            if isinstance(depends_on, str):
                depends_on = [depends_on]

            if len(depends_on) == 1:
                # Jeśli jest tylko jedna zależność, użyj jej wyniku
                dep_step = depends_on[0]
                if dep_step in context['steps'] and 'output' in context['steps'][dep_step]:
                    return context['steps'][dep_step]['output']

            # W przeciwnym razie, zwróć None
            return None

        # Jeśli podano bezpośrednio dane wejściowe
        input_value = step['input']

        # Jeśli to referencja do wyniku innego kroku
        if isinstance(input_value, str) and input_value.startswith('${'):
            return self._resolve_path(input_value, context)

        return input_value

    def _process_outputs(self, output_specs, context):
        """Przetwarza wyniki workflow na podstawie specyfikacji."""
        for spec in output_specs:
            name = spec['name']
            value = spec['value']

            # Sprawdź warunek jeśli podano
            condition = spec.get('condition')
            if condition and not self._evaluate_condition(condition, context):
                continue

            # Rozwiąż wartość
            if isinstance(value, str) and value.startswith('${'):
                resolved_value = self._resolve_path(value, context)
            else:
                resolved_value = value

            context['outputs'][name] = resolved_value

    def _interpolate_string(self, text, context):
        """Interpoluje zmienne w tekście."""
        if not isinstance(text, str):
            return text

        # Znajdź wszystkie wystąpienia ${...}
        pattern = r'\$\{([^}]+)\}'

        def replace_var(match):
            path = match.group(1)
            try:
                value = self._resolve_path(f"${{{path}}}", context)
                if isinstance(value, (dict, list)):
                    return json.dumps(value)
                return str(value)
            except Exception as e:
                return f"${{{path}}}"

        return re.sub(pattern, replace_var, text)

    def _resolve_path(self, path_expr, context):
        """Rozwiązuje wyrażenie ścieżki ${...}."""
        if not isinstance(path_expr, str) or not path_expr.startswith('${') or not path_expr.endswith('}'):
            return path_expr

        # Wyciągnij ścieżkę
        path = path_expr[2:-1].strip()
        parts = path.split('.')

        # Rozwiąż ścieżkę
        current = context
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                current = current[int(part)]
            else:
                raise ValueError(f"Cannot resolve path: {path}")

        return current