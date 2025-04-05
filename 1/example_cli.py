#!/usr/bin/env python3
# example_cli.py

# Import adapter classes
from adapters.BashAdapter import BashAdapter
from adapters.PHPAdapter import PHPAdapter
from adapters.NodeAdapter import NodeAdapter
from adapters.HttpClientAdapter import HttpClientAdapter
from adapters.HttpServerAdapter import HttpServerAdapter
from adapters.PythonAdapter import PythonAdapter
import adapters

bash = BashAdapter('bash')
php = PHPAdapter('php')
node = NodeAdapter('node')
http_client = HttpClientAdapter('http_client')
http_server = HttpServerAdapter('http_server')
python = PythonAdapter('python')

# Słownik dostępnych adapterów
ADAPTERS = {
    'bash': bash,
    'php': php,
    'node': node,
    'http_client': http_client,
    'http_server': http_server,
    'python': python
}

# Create adapter instances
bash = BashAdapter('bash')
python = PythonAdapter('python')
http_client = HttpClientAdapter('http_client')

print("Running example_cli.py")

# Example 1: Listing files and filtering by Python
print("\n--- Example 1: Listing files and filtering ---")
result = bash.command('ls -la').execute()
filtered_result = python.code('''
result = [line for line in input_data.split("\\n") if ".py" in line]
''').execute(result)
print(filtered_result)

# Example 2: Simple bash command
print("\n--- Example 2: Simple bash command ---")
cmd_result = bash.command("echo 'Hello World' > test.txt && cat test.txt").execute()
print(f"Command result: {cmd_result}")

# Example 3: Direct API call (commented out to avoid network errors)
print("\n--- Example 3: API call to JSONPlaceholder ---")
try:
    data = http_client.url('https://jsonplaceholder.typicode.com/todos/1').method('GET').execute()
    print(f"API response: {data}")
except Exception as e:
    print(f"API call failed: {e}")

# Example 4: Pipeline using the engine
print("\n--- Example 4: Using pipeline engine ---")
from pipeline_engine import PipelineEngine

try:
    # Create direct pipeline without dot notation
    from dsl_parser import DotNotationParser
    adapter_call = DotNotationParser.parse('bash.command("echo Simple Test")')
    result = PipelineEngine.execute_adapter_call(adapter_call, None)
    print(f"Direct pipeline result: {result}")
except Exception as e:
    print(f"Pipeline execution failed: {e}")
    import traceback
    traceback.print_exc()