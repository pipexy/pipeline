#!/usr/bin/env python3
# examples/python_adapter_example.py

from adapters.PythonAdapter import PythonAdapter


# Example 1: Simple calculation
def simple_calculation_example():
    print("\n--- Python Adapter Example 1: Simple calculation ---")
    adapter = PythonAdapter({})
    adapter.code("result = 5 * 10")
    result = adapter.execute()
    print(f"Calculation result: {result}")


# Example 2: Using input data
def input_data_example():
    print("\n--- Python Adapter Example 2: Using input data ---")
    adapter = PythonAdapter({})
    adapter.code("result = input_data * 2 if isinstance(input_data, (int, float)) else 'Input is not a number'")
    result = adapter.execute(5)
    print(f"Result with input 5: {result}")

    result = adapter.execute("text")
    print(f"Result with input 'text': {result}")


# Example 3: More complex processing
def complex_processing_example():
    print("\n--- Python Adapter Example 3: Complex processing ---")
    adapter = PythonAdapter({})

    code = """
import json
from datetime import datetime

data = {'timestamp': datetime.now().isoformat(), 'value': input_data}
result = json.dumps(data)
"""
    adapter.code(code)
    result = adapter.execute(42)
    print(f"JSON result: {result}")


if __name__ == "__main__":
    print("Running PythonAdapter examples:")
    simple_calculation_example()
    input_data_example()
    complex_processing_example()