from adapters import rest, json, python, database

# Using JSONPlaceholder - a free testing API instead of the non-existent example.com
try:
    # In api2db.py, ensure your Python code block has consistent indentation:

    result = (rest.get("https://jsonplaceholder.typicode.com/users")
              | json.parse()
              | python.execute("""
    def process_users(users):
        processed_users = []
        for user in users:
            processed_user = {
                'id': user['id'],
                'name': user['name'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'website': user['website']
            }
            processed_users.append(processed_user)
        return process_users(data)
    """)
              | database.connect("users.db")
              .insert("users")
              .execute())

    print(f"Inserted {result.get('inserted', 0)} users")

except Exception as e:
    print(f"Error in pipeline: {e}")
    # For debugging
    import traceback

    traceback.print_exc()