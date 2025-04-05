#!/usr/bin/env python3
# examples/http_server_adapter_example.py

from adapters.HttpServerAdapter import HttpServerAdapter
import time
import threading


# Example 1: Simple HTTP server
def simple_server_example():
    print("\n--- HTTP Server Adapter Example 1: Simple server ---")

    adapter = HttpServerAdapter({})
    adapter.port(8000)
    adapter.host("localhost")

    # Define a simple route
    def hello_handler(request):
        return {"message": "Hello from HttpServerAdapter!"}

    adapter.route("/hello", "GET", hello_handler)

    # Start server in a separate thread so it doesn't block the example
    server_thread = threading.Thread(target=adapter.execute)
    server_thread.daemon = True
    server_thread.start()

    print("Server started at http://localhost:8000")
    print("Try accessing: http://localhost:8000/hello")
    print("Server will run for 10 seconds for this example...")

    # Let the server run for a bit
    time.sleep(10)
    print("Example completed. In a real application, the server would continue running.")


# Example 2: Server with multiple routes and methods
def multi_route_server_example():
    print("\n--- HTTP Server Adapter Example 2: Multiple routes and methods ---")

    adapter = HttpServerAdapter({})
    adapter.port(8000)
    adapter.host("localhost")

    # GET handler
    def get_user_handler(request):
        user_id = request.args.get('id')
        return {"userId": user_id, "name": f"User {user_id}", "method": "GET"}

    # POST handler
    def create_user_handler(request):
        data = request.get_json()
        return {"status": "created", "user": data, "method": "POST"}

    # PUT handler
    def update_user_handler(request):
        user_id = request.args.get('id')
        data = request.get_json()
        return {"status": "updated", "userId": user_id, "newData": data, "method": "PUT"}

    # DELETE handler
    def delete_user_handler(request):
        user_id = request.args.get('id')
        return {"status": "deleted", "userId": user_id, "method": "DELETE"}

    # Register routes
    adapter.route("/user", "GET", get_user_handler)
    adapter.route("/user", "POST", create_user_handler)
    adapter.route("/user", "PUT", update_user_handler)
    adapter.route("/user", "DELETE", delete_user_handler)

    # Start server in a separate thread
    server_thread = threading.Thread(target=adapter.execute)
    server_thread.daemon = True
    server_thread.start()

    print("Server started at http://localhost:8000")
    print("Available endpoints:")
    print("- GET /user?id=123")
    print("- POST /user (with JSON body)")
    print("- PUT /user?id=123 (with JSON body)")
    print("- DELETE /user?id=123")
    print("Server will run for 10 seconds for this example...")

    # Let the server run for a bit
    time.sleep(10)
    print("Example completed. In a real application, the server would continue running.")


# Example 3: Server with static file handling
def static_files_server_example():
    print("\n--- HTTP Server Adapter Example 3: Static file handling ---")

    adapter = HttpServerAdapter({})
    adapter.port(8000)
    adapter.host("localhost")

    # API route
    def api_handler(request):
        return {"status": "active", "timestamp": time.time()}

    adapter.route("/api/status", "GET", api_handler)

    # Serve static files
    adapter.serve_static("/static", "./static_files")

    # Default route to serve index.html
    def index_handler(request):
        return adapter.serve_file("./static_files/index.html")

    adapter.route("/", "GET", index_handler)

    # Start server in a separate thread
    server_thread = threading.Thread(target=adapter.execute)
    server_thread.daemon = True
    server_thread.start()

    print("Server started at http://localhost:8000")
    print("Available endpoints:")
    print("- /api/status - JSON API")
    print("- /static/* - Static files")
    print("- / - Index page")
    print("Server will run for 10 seconds for this example...")

    # Let the server run for a bit
    time.sleep(10)
    print("Example completed. In a real application, the server would continue running.")


if __name__ == "__main__":
    print("Running HttpServerAdapter examples:")
    simple_server_example()
    multi_route_server_example()
    static_files_server_example()