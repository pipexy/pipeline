from adapters import rest, json, python, database

# Using JSONPlaceholder - a free testing API instead of the non-existent example.com
try:
    result = (rest.get("https://jsonplaceholder.typicode.com/users")
              | json.parse()
              | python.code("""
                # Process each user record
                processed_users = []
                for user in input_data:
                    processed_users.append({
                        "user_id": user["id"],
                        "name": user["name"],
                        "email": user["email"].lower(),
                        "active": True
                    })
                output = processed_users
              """)
              | database.connect("users.db")
              .insert("users")
              .execute())  # Only execute at the end of the pipeline

    print(f"Inserted {result.get('inserted', 0)} users")

except Exception as e:
    print(f"Error in pipeline: {e}")
    # For debugging
    import traceback

    traceback.print_exc()