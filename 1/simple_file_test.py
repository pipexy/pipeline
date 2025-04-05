# simple_file_test.py

import datetime

try:
    # Create some test content
    test_content = "# File Writing Test\n\n"
    test_content += "This is a simple test using Python's built-in file operations.\n"
    test_content += "If you can see this text, basic file writing is working.\n\n"
    test_content += f"Test completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Write to file using standard Python file operations
    with open("simple_test_output.md", "w") as file:
        file.write(test_content)

    print(f"Test content successfully written to simple_test_output.md")
    print(f"Check the file to verify it contains the test content")

except Exception as e:
    print(f"Error writing file: {e}")