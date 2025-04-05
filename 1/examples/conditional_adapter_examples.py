#!/usr/bin/env python3
# examples/conditional_adapter_example.py

from adapters.conditional_adapter import ConditionalAdapter
from adapters.PythonAdapter import PythonAdapter
from adapters.BashAdapter import BashAdapter


# Example 1: Basic condition with different branches
def basic_condition_example():
    print("\n--- Conditional Adapter Example 1: Basic condition ---")

    # Create the conditional adapter
    conditional = ConditionalAdapter({})

    # Set the condition
    conditional.condition("input_data > 10")

    # Create true branch adapter
    true_adapter = PythonAdapter({})
    true_adapter.code("result = 'Value is greater than 10'")

    # Create false branch adapter
    false_adapter = PythonAdapter({})
    false_adapter.code("result = 'Value is less than or equal to 10'")

    # Set the branches
    conditional.if_true(true_adapter)
    conditional.if_false(false_adapter)

    # Execute with different inputs
    print(f"Result with input 5: {conditional.execute(5)}")
    print(f"Result with input 15: {conditional.execute(15)}")


# Example 2: Type-based condition
def type_condition_example():
    print("\n--- Conditional Adapter Example 2: Type-based condition ---")

    # Create the conditional adapter
    conditional = ConditionalAdapter({})

    # Set the condition to check type
    conditional.condition("isinstance(input_data, str)")

    # Create true branch adapter (for strings)
    true_adapter = PythonAdapter({})
    true_adapter.code("result = f'String received: {input_data}'")

    # Create false branch adapter (for non-strings)
    false_adapter = PythonAdapter({})
    false_adapter.code("result = f'Non-string received: {input_data}'")

    # Set the branches
    conditional.if_true(true_adapter)
    conditional.if_false(false_adapter)

    # Execute with different inputs
    print(f"Result with input 'hello': {conditional.execute('hello')}")
    print(f"Result with input 42: {conditional.execute(42)}")


# Example 3: Different adapter types in branches
def mixed_adapters_example():
    print("\n--- Conditional Adapter Example 3: Mixed adapter types ---")

    # Create the conditional adapter
    conditional = ConditionalAdapter({})

    # Set the condition
    conditional.condition("input_data == 'bash'")

    # Create bash adapter for true branch
    true_adapter = BashAdapter({})
    true_adapter.command("echo 'Executing bash command'")

    # Create python adapter for false branch
    false_adapter = PythonAdapter({})
    false_adapter.code("result = 'Executing Python code'")

    # Set the branches
    conditional.if_true(true_adapter)
    conditional.if_false(false_adapter)

    # Execute with different inputs
    print(f"Result with input 'bash': {conditional.execute('bash')}")
    print(f"Result with input 'python': {conditional.execute('python')}")


if __name__ == "__main__":
    print("Running ConditionalAdapter examples:")
    basic_condition_example()
    type_condition_example()
    mixed_adapters_example()