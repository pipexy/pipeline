# Interfejs linii poleceń
"""
cli.py
"""

# cli.py
import argparse
import json
import sys
import os
from datetime import datetime
from pipeline_dsl import PipelineDSL


def main():
    parser = argparse.ArgumentParser(description="Run service pipelines")
    parser.add_argument("command", choices=["run", "list", "serve"], help="Command to execute")
    parser.add_argument("--pipeline", "-p", help="Pipeline name to run")
    parser.add_argument("--file", "-f", default="pipelines.yaml", help="Pipeline definition file (YAML)")
    parser.add_argument("--input", "-i", help="Input data JSON file or string")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--param", "-P", action="append", help="Pipeline parameters (format: key=value)")
    parser.add_argument("--port", type=int, default=5000, help="Server port (for serve command)")

    args = parser.parse_args()

    # Obsługa parametrów
    params = {}
    if args.param:
        for param in args.param:
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value

    # Dodaj dynamiczne parametry
    params['today'] = datetime.now().strftime('%Y-%m-%d')
    params['timestamp'] = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Obsługa poleceń
    if args.command == "list":
        list_pipelines(args.file)
    elif args.command == "run":
        run_pipeline(args.file, args.pipeline, args.input, args.output, params)
    elif args.command == "serve":
        serve_pipelines(args.file, args.port)


def list_pipelines(file_path):
    """Wyświetla listę dostępnych pipeline'ów."""
    try:
        config = PipelineDSL.load_from_yaml(file_path)

        if 'pipelines' not in config:
            print(f"Error: No pipelines found in {file_path}")
            sys.exit(1)

        print(f"Available pipelines in {file_path}:")
        print("-" * 50)

        for name, pipeline in config['pipelines'].items():
            print(f"- {name}")
            if 'description' in pipeline:
                print(f"  Description: {pipeline['description']}")
            print(f"  Steps: {len(pipeline.get('steps', []))}")
            print()

    except Exception as e:
        print(f"Error listing pipelines: {e}")
        sys.exit(1)


def run_pipeline(file_path, pipeline_name, input_path, output_path, params):
    """Uruchamia pipeline z podanymi parametrami."""
    try:
        # Pobierz dane wejściowe
        input_data = None
        if input_path:
            if os.path.exists(input_path):
                with open(input_path, 'r') as f:
                    input_data = json.load(f)
            else:
                # Traktuj jako string JSON
                try:
                    input_data = json.loads(input_path)
                except json.JSONDecodeError:
                    input_data = input_path

        # Uruchom pipeline
        result = PipelineDSL.run_pipeline_from_file(
            file_path,
            pipeline_name,
            input_data
        )

        # Zapisz wynik lub wyświetl na konsoli
        if output_path:
            directory = os.path.dirname(output_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Zastąp placeholdery w ścieżce wyjściowej
            for key, value in params.items():
                output_path = output_path.replace(f"{{{key}}}", value)

            with open(output_path, 'w') as f:
                if isinstance(result, (dict, list)):
                    json.dump(result, f, indent=2)
                else:
                    f.write(str(result))

            print(f"Output saved to: {output_path}")
        else:
            if isinstance(result, (dict, list)):
                print(json.dumps(result, indent=2))
            else:
                print(result)

    except Exception as e:
        print(f"Error running pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def serve_pipelines(file_path, port):
    """Uruchamia serwer HTTP udostępniający pipeline'y."""
    from flask import Flask, request, jsonify
    import threading

    app = Flask(__name__)

    # Ładuj pipeline'y
    try:
        config = PipelineDSL.load_from_yaml(file_path)
        if 'pipelines' not in config:
            print(f"Error: No pipelines found in {file_path}")
            sys.exit(1)

        pipelines = config['pipelines']
        print(f"Loaded {len(pipelines)} pipelines from {file_path}")

    except Exception as e:
        print(f"Error loading pipelines: {e}")
        sys.exit(1)

    @app.route('/pipelines', methods=['GET'])
    def list_available_pipelines():
        return jsonify({
            'pipelines': [
                {
                    'name': name,
                    'description': pipeline.get('description', ''),
                    'steps': len(pipeline.get('steps', []))
                }
                for name, pipeline in pipelines.items()
            ]
        })

    @app.route('/pipelines/<pipeline_name>', methods=['POST'])
    def execute_pipeline(pipeline_name):
        if pipeline_name not in pipelines:
            return jsonify({'error': f'Pipeline {pipeline_name} not found'}), 404

        try:
            # Pobierz dane wejściowe
            input_data = request.json

            # Uruchom pipeline
            result = PipelineDSL.execute_pipeline(
                pipelines[pipeline_name],
                input_data
            )

            return jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Uruchom serwer
    print(f"Pipeline server running at http://127.0.0.1:{port}")
    print("Available endpoints:")
    print(f"  GET  /pipelines            - List all pipelines")
    print(f"  POST /pipelines/PIPELINE   - Execute a pipeline")
    app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    main()