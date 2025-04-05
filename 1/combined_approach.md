
content = "# File Writing Test\n\n"
content += "This is a pipeline test.\n"
content += "Current time: " + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
content  # Last expression is evaluated as the result
