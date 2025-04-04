# pipeline_engine.py
"""
Silnik wykonujący sekwencje adapterów
"""

from dsl_parser import DotNotationParser, YamlDSLParser
from adapters_extended import ADAPTERS


class PipelineEngine:
    """Silnik wykonujący pipeline'y w DSL."""

    @staticmethod
    def execute_adapter_call(adapter_call, input_data=None):
        """Wykonuje pojedyncze wywołanie adaptera."""
        adapter_name = adapter_call['adapter']
        methods = adapter_call['methods']

        # Pobierz adapter
        if adapter_name not in ADAPTERS:
            raise ValueError(f"Unknown adapter: {adapter_name}")

        adapter = ADAPTERS[adapter_name]
        adapter.reset()  # Reset adaptera przed użyciem

        # Zastosuj wszystkie metody
        for method in methods:
            method_name = method['name']
            value = method['value']

            # Wywołaj metodę
            getattr(adapter, method_name)(value)

        # Wykonaj adapter
        return adapter.execute(input_data)

    @staticmethod
    def execute_pipeline(pipeline, initial_input=None):
        """Wykonuje sekwencję kroków pipeline'a."""
        result = initial_input

        for step in pipeline:
            adapter_call = step
            result = PipelineEngine.execute_adapter_call(adapter_call, result)

        return result

    @staticmethod
    def execute_from_dot_notation(expression, initial_input=None):
        """Wykonuje pipeline z wyrażenia w notacji kropkowej."""
        # Rozdziel wyrażenie na kroki (po kropce poza nawiasami)
        steps = []
        current = ""
        bracket_count = 0

        for char in expression:
            if char == '(':
                bracket_count += 1
                current += char
            elif char == ')':
                bracket_count -= 1
                current += char
            elif char == '.' and bracket_count == 0:
                if current:
                    steps.append(current)
                    current = ""
            else:
                current += char

        if current:
            steps.append(current)

        # Parsuj i wykonaj każdy krok
        result = initial_input
        for step_expr in steps:
            adapter_call = DotNotationParser.parse(step_expr)
            result = PipelineEngine.execute_adapter_call(adapter_call, result)

        return result

    @staticmethod
    def execute_from_yaml(yaml_def, pipeline_name=None, initial_input=None):
        """Wykonuje pipeline z definicji YAML."""
        config = yaml_def
        if isinstance(yaml_def, str):
            config = YamlDSLParser.parse(yaml_def)

        if 'pipelines' not in config:
            raise ValueError("YAML must contain 'pipelines' key")

        # Wybierz pipeline
        if pipeline_name:
            if pipeline_name not in config['pipelines']:
                raise ValueError(f"Pipeline '{pipeline_name}' not found")
            pipeline = config['pipelines'][pipeline_name]
        else:
            # Użyj pierwszego pipeline'a
            pipeline_name = next(iter(config['pipelines']))
            pipeline = config['pipelines'][pipeline_name]

        # Wykonaj pipeline
        return PipelineEngine.execute_pipeline(pipeline['steps'], initial_input)