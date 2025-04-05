#!/usr/bin/env python3
# examples/chainable_adapter_example.py

from adapters.ChainableAdapter import ChainableAdapter
from adapters.BashAdapter import BashAdapter
from adapters.PythonAdapter import PythonAdapter
from adapters.HttpClientAdapter import HttpClientAdapter


# Example 1: Chain bash and python adapters
def bash_to_python_example():
    print("\n--- Chainable Adapter Example 1: Bash to Python chain ---")

    # Create the chainable adapter
    chain = ChainableAdapter({})

    # Create and configure bash adapter
    bash = BashAdapter({})
    bash.command("echo 'Hello from Bash!'")

    # Create and configure python adapter
    python = PythonAdapter({})
    python.code("result = f'Python processed: {input_data.strip()}'")

    # Add adapters to the chain
    chain.add(bash)
    chain.add(python)

    # Execute the chain
    result = chain.execute()
    print(f"Chain result: {result}")


# Example 2: API call with processing
def api_processing_example():
    print("\n--- Chainable Adapter Example 2: API call with processing ---")

    # Create the chainable adapter
    chain = ChainableAdapter({})

    # Create and configure HTTP client adapter
    http = HttpClientAdapter({})
    http.url("https://jsonplaceholder.typicode.com/todos/1")

    # Create and configure python adapter for processing
    python = PythonAdapter({})
    python.code("""
import json
data = json.loads(input_data)
result = f"Todo #{data['id']}: {data['title']} (Completed: {data['completed']})"
""")

    # Add adapters to the chain
    chain.add(http)
    chain.add(python)

    # Execute the chain
    result = chain.execute()
    print(f"Processed API result: {result}")


# Example 3: Multi-step processing chain
def multi_step_example():
    print("\n--- Chainable Adapter Example 3: Multi-step processing chain ---")

    # Create the chainable adapter
    chain = ChainableAdapter({})

    # Step 1: Get data with bash
    bash = BashAdapter({})
    bash.command("date")

    # Step 2: Format with Python
    python1 = PythonAdapter({})
    python1.code("result = f'Current date: {input_data.strip()}'")

    # Step 3: Add more info with Python
    python2 = PythonAdapter({})
    python2.code("""
import platform
result = f"{input_data} | System: {platform.system()} {platform.release()}"
""")

    # Add all adapters to the chain
    chain.add(bash)
    chain.add(python1)
    chain.add(python2)

    # Execute the chain
    result = chain.execute()
    print(f"Final chain result: {result}")


if __name__ == "__main__":
    print("Running ChainableAdapter examples:")
    bash_to_python_example()
    api_processing_example()
    multi_step_example()