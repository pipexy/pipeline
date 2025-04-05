# file_write_test.py
from adapters import python, file

try:
    # Create some simple test content
    result = (python.execute("""
# Generate simple test content
test_content = "# File Writing Test\\n\\n"
test_content += "This is a simple test of the file adapter.\\n"
test_content += "If you can see this text in the output file, the file adapter is working correctly.\\n"
test_content += "\\n"
test_content += "Test completed at: " + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')

result = test_content
""")
              | file.write("test_output.md")
              .execute())

    print(f"Test content successfully written to test_output.md")
    print(f"Check the file to verify it contains the test content")

except Exception as e:
    print(f"Error in file writing test: {e}")
    import traceback
    traceback.print_exc()