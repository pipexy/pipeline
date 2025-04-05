#!/usr/bin/env python3
# examples/http_client_adapter_example.py

from adapters.HttpClientAdapter import HttpClientAdapter


# Example 1: Simple GET request
def simple_get_example():
    print("\n--- HTTP Client Adapter Example 1: Simple GET request ---")
    adapter = HttpClientAdapter({})
    adapter.url("https://jsonplaceholder.typicode.com/todos/1")
    result = adapter.execute()
    print(f"API response: {result}")


# Example 2: POST request with JSON data
def post_with_json_example():
    print("\n--- HTTP Client Adapter Example 2: POST request with JSON data ---")
    adapter = HttpClientAdapter({})
    adapter.url("https://jsonplaceholder.typicode.com/posts")
    adapter.method("POST")
    adapter.headers({"Content-Type": "application/json"})
    adapter.data({
        "title": "Test Post",
        "body": "This is a test post created with HttpClientAdapter",
        "userId": 1
    })
    result = adapter.execute()
    print(f"POST response: {result}")


# Example 3: Request with custom headers
def custom_headers_example():
    print("\n--- HTTP Client Adapter Example 3: Request with custom headers ---")
    adapter = HttpClientAdapter({})
    adapter.url("https://httpbin.org/headers")
    adapter.headers({
        "X-Custom-Header": "Custom Value",
        "User-Agent": "PipelineHttpClient/1.0"
    })
    result = adapter.execute()
    print(f"Headers echo response: {result}")


if __name__ == "__main__":
    print("Running HttpClientAdapter examples:")
    simple_get_example()
    post_with_json_example()
    custom_headers_example()