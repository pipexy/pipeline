# approach1.py
from adapters import python, file

try:

    # read from one and save to another file
    (
    file.read("first.md")
    | file.write("second.md").execute()
    )

    print("Content written directly successfully!")
except Exception as e:
    print(f"Error: {e}")