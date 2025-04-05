from adapters.RESTAdapter import RESTAdapter
from adapters.JSONAdapter import JSONAdapter
from adapters.PythonAdapter import PythonAdapter
from adapters.DatabaseAdapter import DatabaseAdapter

# Create a data processing pipeline
result = (RESTAdapter()
    .get("https://api.example.com/users")
    .headers({"Accept": "application/json"})
    ._execute_self()
    | JSONAdapter()
    .parse_string()
    .select("$.users[*]")
    ._execute_self()
    | PythonAdapter()
    .code("""
        # Process each user record
        processed_users = []
        for user in input_data:
            processed_users.append({
                "user_id": user["id"],
                "full_name": f"{user['first_name']} {user['last_name']}",
                "email": user["email"].lower(),
                "active": True
            })
        output = processed_users
    """)
    ._execute_self()
    | DatabaseAdapter()
    .connect("users.db")
    ._execute_self()
    .insert("users")
    ._execute_self())

print(f"Inserted {result['inserted']} users")