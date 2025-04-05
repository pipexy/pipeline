# pipeline_dsl.py
import yaml
import json
from adapters_extended import ADAPTERS


class PipelineDSL:
    """Parser i wykonywanie pipeline'ów z YAML."""

    @staticmethod
    def load_from_yaml(yaml_path):
        """Ładuje pipeline z pliku YAML."""
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)

    @staticmethod
    def execute_pipeline(pipeline_def, initial_input=None):
        """Wykonuje pipeline na podstawie definicji."""
        if not pipeline_def or not isinstance(pipeline_def, dict):
            raise ValueError("Invalid pipeline definition")

        steps = pipeline_def.get('steps', [])
        result = initial_input

        for step in steps:
            adapter_name = step.get('adapter')
            if not adapter_name or adapter_name not in ADAPTERS:
                raise ValueError(f"Unknown adapter: {adapter_name}")

            # Pobierz adapter
            adapter = ADAPTERS[adapter_name]
            adapter.reset()

            # Zastosuj metody
            methods = step.get('methods', [])
            for method in methods:
                method_name = method.get('name')
                method_value = method.get('value')

                if not method_name:
                    continue

                # Wywołaj metodę
                getattr(adapter, method_name)(method_value)

            # Wykonaj adapter
            result = adapter.execute(result)

        return result

    @staticmethod
    def run_pipeline_from_file(yaml_path, pipeline_name=None, initial_input=None):
        """Uruchamia pipeline z pliku YAML."""
        config = PipelineDSL.load_from_yaml(yaml_path)

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
        return PipelineDSL.execute_pipeline(pipeline, initial_input)