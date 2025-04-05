#!/usr/bin/env python3

# test_parser.py

from dsl_parser import DotNotationParser
from adapters import ADAPTERS

# Test the parser directly
expression = 'bash.command("echo test > test.txt && cat test.txt")'
print(f"Testing expression: {expression}")

parsed = DotNotationParser.parse(expression)
print(f"Parsed result: {parsed}")

# Get the adapter
adapter_name = parsed['adapter']
if adapter_name not in ADAPTERS:
    print(f"Error: Unknown adapter '{adapter_name}'")
    exit(1)

adapter = ADAPTERS[adapter_name]
print(f"Found adapter: {adapter.name}")

# Apply methods
methods = parsed['methods']
print(f"Methods to apply: {methods}")

for method in methods:
    method_name = method['name']
    value = method['value']
    print(f"Applying method: {method_name} with value: {value}")
    method_func = getattr(adapter, method_name, None)
    if method_func is None:
        print(f"Error: Method '{method_name}' not found on adapter '{adapter_name}'")
        exit(1)
    method_func(value)

# Check if command is set
print(f"Adapter params: {adapter._params}")

# Execute
result = adapter.execute()
print(f"Execution result: {result}")