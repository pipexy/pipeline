# dsl_parser.py
import re
import yaml
import ast
from typing import Dict, Any, List, Union, Callable


class DotNotationParser:
    """Parser dla wyrażeń w notacji kropkowej z metodami."""

    @staticmethod
    def _parse_arguments(arg_str):
        """Parsuje argumenty metody."""
        # Próba parsowania jako wyrażenie Pythona
        try:
            # Zawijamy w nawiasy, aby ast.literal_eval potraktował to jako tuple
            wrapped = f"({arg_str})"
            args = ast.literal_eval(wrapped)

            # Jeśli to pojedyncza wartość, zwróć ją
            if isinstance(args, tuple) and len(args) == 1:
                return args[0]
            return args
        except (SyntaxError, ValueError):
            # Jeśli nie można sparsować jako literał, zwróć jako string
            return arg_str

    @staticmethod
    def parse(expression):
        """Parsuje wyrażenie w notacji kropkowej."""
        # Regex dla wyrażenia: adapter.method(arg).method2(arg2)
        adapter_pattern = r'([a-zA-Z0-9_-]+)(?:\.(.*?))?'
        adapter_match = re.match(adapter_pattern, expression)

        if not adapter_match:
            raise ValueError(f"Invalid syntax: {expression}")

        adapter_name = adapter_match.group(1)

        # Jeśli nie ma metod, zwróć sam adapter
        if not adapter_match.group(2):
            return {
                'adapter': adapter_name,
                'methods': []
            }

        # Regex dla metod: method1('arg1').method2(arg2)
        method_pattern = r'([a-zA-Z0-9_-]+)\s*\(([^)]*)\)'
        method_matches = re.finditer(method_pattern, adapter_match.group(2))

        methods = []
        for match in method_matches:
            method_name = match.group(1)
            arg_str = match.group(2).strip()

            # Parsuj argumenty
            arg_value = DotNotationParser._parse_arguments(arg_str)

            methods.append({
                'name': method_name,
                'value': arg_value
            })

        return {
            'adapter': adapter_name,
            'methods': methods
        }


class YamlDSLParser:
    """Parser dla DSL w formacie YAML."""

    @staticmethod
    def parse_file(file_path):
        """Parsuje plik YAML z definicją pipeline'ów."""
        with open(file_path, 'r') as f:
            content = f.read()
        return YamlDSLParser.parse(content)

    @staticmethod
    def parse(yaml_content):
        """Parsuje zawartość YAML."""
        try:
            config = yaml.safe_load(yaml_content)
            return config
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML: {e}")