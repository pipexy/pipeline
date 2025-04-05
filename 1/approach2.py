# debug_pipeline.py
from adapters import python, file


def run_pipeline(steps):
    result = None
    for i, step in enumerate(steps):
        print(f"Step {i}: Input = {type(result)}")
        result = step(result)
        print(f"Step {i}: Output = {type(result)}")
    return result

def generate_content(_):
    print("Generating content...")
    script = """
# Create the content string
content = "# Generated Content\\n\\n"
content += "Created at: " + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# The last expression will be the result
content  # Last expression is what gets returned
"""
    adapter = python.execute(script)
    print(f"Adapter type: {type(adapter)}")
    print(f"Adapter has execute method: {hasattr(adapter, 'execute')}")

    result = adapter.execute()
    print(f"Result from execute(): {type(result)}")
    print(f"Result content: {result if result else 'None'}")
    return result

def save_to_file(content, filename="output.md"):
    if content is None:
        print("Warning: Content is None, cannot save")
        return None

    print(f"Saving content: {content[:30]}...")
    file_adapter = file.write(filename, content)
    file_adapter.execute()
    return content



if __name__ == "__main__":
    try:
        pipeline = [
            generate_content,
            lambda content: save_to_file(content, "pipeline_output.md")
        ]

        result = run_pipeline(pipeline)

        # Safely print the result
        if result:
            print(f"Success! Content: {result[:30]}...")
        else:
            print("Warning: Result is None")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()