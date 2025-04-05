# pipeline_test_fixed.py
from adapters import python, file

try:
    # Method 2: Use proper data passing between pipeline stages
    (
        python.execute("""
# Generate content
return "# Pipeline Test\\n\\nThis text was created in a pipeline at " + 
       __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
""")
        .pipe(lambda content: file.write("pipeline_output1.md", content).execute())
    )

    print("Pipeline executed successfully!")

except Exception as e:
    print(f"Error in pipeline: {e}")
    import traceback

    traceback.print_exc()
