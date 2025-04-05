#!/usr/bin/env python3
# examples/bash_adapter_example.py

from adapters.BashAdapter import BashAdapter


# Example 1: Simple command execution
def simple_command_example():
    print("\n--- Bash Adapter Example 1: Simple command execution ---")
    adapter = BashAdapter({})
    adapter.command("echo 'Hello from Bash!'")
    result = adapter.execute()
    print(f"Command result: {result}")


# Example 2: Command with arguments
def command_with_args_example():
    print("\n--- Bash Adapter Example 2: Command with arguments ---")
    adapter = BashAdapter({})
    adapter.command("ls -la")
    result = adapter.execute()
    print(f"Directory listing:\n{result}")


# Example 3: Pipeline command
def pipeline_command_example():
    print("\n--- Bash Adapter Example 3: Pipeline command ---")
    adapter = BashAdapter({})
    adapter.command("cat /etc/passwd | grep root")
    result = adapter.execute()
    print(f"Filtered result:\n{result}")


if __name__ == "__main__":
    print("Running BashAdapter examples:")
    simple_command_example()
    command_with_args_example()
    pipeline_command_example()