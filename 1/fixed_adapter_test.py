# fixed_adapter_test.py
from adapters import python, file
import io
import sys

try:
    # Capture stdout to get the print output
    original_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output

    # Execute the Python code
    python.execute("print('Hello World')")

    # Get the captured output and restore stdout
    sys.stdout = original_stdout
    output = captured_output.getvalue().strip()

    # Write the output to file
    with open("fixed_test_output.md", "w") as f:
        f.write(output)

    print("Content written successfully!")
except Exception as e:
    # Restore stdout in case of exception
    if 'original_stdout' in locals():
        sys.stdout = original_stdout
    print(f"Error: {e}")