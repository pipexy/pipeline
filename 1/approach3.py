# approach3.py
from adapters import python, file

try:
    python.execute("""
content = "# File Writing Test\\n\\n"
content += "This is a test with pipe method.\\n"
content += "Current time: " + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
return content
""").pipe(
        lambda content: file.write("pipe_output1.md", content).execute()
    )

    print("Pipe method execution successful!")
except Exception as e:
    print(f"Error: {e}")