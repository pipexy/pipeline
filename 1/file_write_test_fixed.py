# file_write_test_fixed.py
from adapters import python, file

try:
    # Create the pipeline with proper data flow
    result = (python.execute("""
# Generate test content
test_content = "# File Writing Test\\n\\n"
test_content += "This is a test of the file adapter.\\n"
test_content += "Current time: " + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# This variable will be used as the output of this step
result = test_content
""")
              | file.write("test_output.md")
              .execute())

    print("Pipeline executed successfully!")
    print("Check test_output.md for the content")

except Exception as e:
    print(f"Pipeline error: {e}")
    import traceback
    traceback.print_exc()