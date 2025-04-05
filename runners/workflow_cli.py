# CLI dla workflow
"""
workflow_cli.py
"""

# workflow_cli.py
import argparse
import json
import sys
import os
from datetime import datetime
from workflow_engine import WorkflowEngine


def main():
    parser = argparse.ArgumentParser(description='Execute workflow pipelines')
    parser.add_argument('command', choices=['run', 'list', 'info', 'validate'],
                        help='Command to execute')
    parser.add_argument('--workflow', '-w', help='Workflow file path')
    parser.add_argument('--input', '-i', help='Input data JSON file or string')
    parser.add_argument('--output', '-o', help='Output file path for results')
    parser.add_argument('--param', '-p', action='append', help='Parameters (format: key=value)')

    args = parser.parse_args()

    # Inicjalizacja silnika workflow
    engine = WorkflowEngine()

    # Obsługa poleceń
    if args.command == 'list':
        list_workflows()
    elif args.command == 'info':
        show_workflow_info(args.workflow, engine)
    elif args.command == 'validate':
        validate_workflow(args.workflow, engine)
    elif args.command == 'run':
        run_workflow(args.workflow, args.input, args.output, args.param, engine)
    else:
        parser.print_help()


def list_workflows():
    """Lista dostępnych workflow w katalogu workflows."""
    workflow_dir = os.path.join(os.getcwd(), 'workflows')
    if not os.path.exists(workflow_dir):
        print(f"Workflows directory not found: {workflow_dir}")
        return

    workflow_files = [f for f in os.listdir(workflow_dir)
                      if f.endswith('.yaml') or f.endswith('.yml')]

    if not workflow_files:
        print("No workflow files found.")
        return

    print(f"Found {len(workflow_files)} workflows:")
    for wf in workflow_files:
        print(f"  - {wf}")
        try:
            with open(os.path.join(workflow_dir, wf), 'r') as f:
                content = f.read()
                if 'name:' in content:
                    name = content.split('name:')[1].split('\n')[0].strip()
                    print(f"    Name: {name}")
                if 'description:' in content:
                    desc = content.split('description:')[1].split('\n')[0].strip()
                    print(f"    Description: {desc}")
        except:
            pass
        print()


def show_workflow_info(workflow_path, engine):
    """Wyświetla szczegóły workflow."""
    if not workflow_path:
        print("Error: Workflow path not specified")
        sys.exit(1)

    try:
        workflow_id = engine.load_workflow(workflow_path)
        workflow = engine.workflows[workflow_id]

        print(f"Workflow: {workflow.get('name', workflow_id)}")
        print(f"Description: {workflow.get('description', 'No description')}")
        print(f"Version: {workflow.get('version', 'N/A')}")
        print()

        # Wyświetl parametry wejściowe
        inputs = workflow.get('inputs', [])
        if inputs:
            print("Inputs:")
            for inp in inputs:
                req = "(required)" if inp.get('required', False) else ""
                default = f" (default: {inp.get('default', 'None')})" if 'default' in inp else ""
                print(f"  - {inp['name']}: {inp.get('type', 'any')} {req}{default}")
                if 'description' in inp:
                    print(f"    Description: {inp['description']}")
            print()

        # Wyświetl kroki
        steps = workflow.get('steps', [])
        if steps:
            print(f"Steps: {len(steps)}")
            for i, step in enumerate(steps):
                print(f"  {i + 1}. {step['id']}: {step.get('adapter', 'unknown')}")
                if 'description' in step:
                    print(f"     {step['description']}")
                if 'depends_on' in step:
                    deps = step['depends_on']
                    if isinstance(deps, list):
                        print(f"     Depends on: {', '.join(deps)}")
                    else:
                        print(f"     Depends on: {deps}")
            print()

        # Wyświetl wyniki
        outputs = workflow.get('outputs', [])
        if outputs:
            print("Outputs:")
            for out in outputs:
                print(f"  - {out['name']}: {out['value']}")
            print()

    except Exception as e:
        print(f"Error showing workflow info: {e}")
        sys.exit(1)


def validate_workflow(workflow_path, engine):
    """Waliduje workflow bez wykonywania go."""
    if not workflow_path:
        print("Error: Workflow path not specified")
        sys.exit(1)

    try:
        workflow_id = engine.load_workflow(workflow_path)
        workflow = engine.workflows[workflow_id]

        # Sprawdź zależności
        engine._build_dependency_graph(workflow.get('steps', []))

        # Sprawdź kompletność
        for step in workflow.get('steps', []):
            if 'id' not in step:
                raise ValueError("Step missing 'id' field")
            if 'adapter' not in step:
                raise ValueError(f"Step {step['id']} missing 'adapter' field")

        print(f"Workflow '{workflow.get('name', workflow_id)}' is valid!")

        # Sprawdź wymagane parametry
        required_inputs = [inp['name'] for inp in workflow.get('inputs', [])
                           if inp.get('required', False)]

        if required_inputs:
            print(f"\nRequired inputs: {', '.join(required_inputs)}")

        # Sprawdź, czy wszystkie adaptery są dostępne
        adapters = set(step['adapter'] for step in workflow.get('steps', []))
        missing_adapters = [a for a in adapters if a not in ADAPTERS]

        if missing_adapters:
            print(f"\nWarning: Missing adapters: {', '.join(missing_adapters)}")

    except Exception as e:
        print(f"Error validating workflow: {e}")
        sys.exit(1)


def run_workflow(workflow_path, input_path, output_path, params, engine):
    """Uruchamia workflow z podanymi parametrami."""
    if not workflow_path:
        print("Error: Workflow path not specified")
        sys.exit(1)

    try:
        # Załaduj workflow
        workflow_id = engine.load_workflow(workflow_path)

        # Przygotuj dane wejściowe
        inputs = {}

        # Z pliku lub string JSON
        if input_path:
            if os.path.exists(input_path):
                with open(input_path, 'r') as f:
                    inputs.update(json.load(f))
            else:
                try:
                    inputs.update(json.loads(input_path))
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON input")
                    sys.exit(1)

        # Z parametrów linii poleceń
        if params:
            for param in params:
                if '=' in param:
                    key, value = param.split('=', 1)

                    # Konwersja wartości
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                        value = float(value)

                    inputs[key] = value

        print(f"Executing workflow: {workflow_id}")
        start_time = datetime.now()

        # Wykonaj workflow
        result = engine.execute_workflow(workflow_id, inputs)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"Workflow execution completed in {duration:.2f} seconds")

        # Wyświetl wyniki
        if 'outputs' in result and result['outputs']:
            print("\nOutputs:")
            for key, value in result['outputs'].items():
                print(f"  - {key}: {value}")

        # Zapisz wyniki do pliku
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nFull results saved to: {output_path}")

        return result

    except Exception as e:
        print(f"Error executing workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()