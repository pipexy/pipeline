# cli.py
import argparse
import json
import sys
from pipeline_engine import PipelineEngine
from dsl_parser import YamlDSLParser


def main():
    parser = argparse.ArgumentParser(description='Execute DSL pipelines')
    parser.add_argument('--pipeline', '-p', help='Pipeline in dot notation')
    parser.add_argument('--yaml', '-y', help='Path to YAML pipeline file')
    parser.add_argument('--pipeline-name', '-n', help='Pipeline name in YAML file')
    parser.add_argument('--input', '-i', help='Input data (JSON string or file path)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')

    args = parser.parse_args()

    # Sprawdź czy podano pipeline
    if not args.pipeline and not args.yaml:
        parser.error("Either --pipeline or --yaml is required")

    # Pobierz dane wejściowe
    input_data = None
    if args.input:
        # Sprawdź czy to plik czy string JSON
        if args.input.startswith('{') or args.input.startswith('['):
            try:
                input_data = json.loads(args.input)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON input", file=sys.stderr)
                sys.exit(1)
        else:
            # Spróbuj odczytać plik
            try:
                with open(args.input, 'r') as f:
                    try:
                        input_data = json.load(f)
                    except json.JSONDecodeError:
                        # Jeśli nie JSON, odczytaj jako tekst
                        f.seek(0)
                        input_data = f.read()
            except IOError as e:
                print(f"Error reading input file: {e}", file=sys.stderr)
                sys.exit(1)

    # Wykonaj pipeline
    try:
        if args.pipeline:
            result = PipelineEngine.execute_from_dot_notation(args.pipeline, input_data)
        else:  # args.yaml
            yaml_config = YamlDSLParser.parse_file(args.yaml)
            result = PipelineEngine.execute_from_yaml(yaml_config, args.pipeline_name, input_data)

        # Zapisz/wyświetl wynik
        if args.output:
            with open(args.output, 'w') as f:
                if isinstance(result, (dict, list)):
                    json.dump(result, f, indent=2)
                else:
                    f.write(str(result))
        else:
            if isinstance(result, (dict, list)):
                print(json.dumps(result, indent=2))
            else:
                print(result)

    except Exception as e:
        print(f"Error executing pipeline: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()