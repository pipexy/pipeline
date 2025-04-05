# Przykład łańcuchowania adapterów
"""
simple_adapter_chaining.py
"""

"""
Przykład prostego łańcuchowania adapterów.
"""

from adapters import bash, python, file_adapter


def main():
    """Przykład użycia adapterów w łańcuchu."""
    # Przykład 1: Przetwarzanie listy plików
    result = bash.command('ls -la') \
        .python.code('''
            # Filtruj tylko pliki Python
            lines = input_data.split('\\n')
            python_files = [line for line in lines if line.endswith('.py')]
            result = python_files
        ''') \
        .file.path('./output/python_files.txt').operation('write') \
        .execute()

    print(f"Lista plików Python zapisana do: {result['path']}")

    # Przykład 2: Pobieranie danych JSON i ich przetwarzanie
    from adapters import http_client

    data = http_client.url('https://jsonplaceholder.typicode.com/posts') \
        .method('GET') \
        .python.code('''
            # Filtruj posty po ID użytkownika
            filtered_posts = [post for post in input_data if post['userId'] == 1]
            result = filtered_posts
        ''') \
        .execute()

    print(f"Pobrano {len(data)} postów użytkownika 1")

    # Przykład 3: Tworzenie prostego API
    from adapters import http_server
    import threading

    api = http_server.path('/api/hello').methods(['GET']).code('''
        def request_handler(input_data):
            import datetime
            return {
                'message': 'Hello World!',
                'timestamp': datetime.datetime.now().isoformat()
            }
        ''').execute()

    print(f"API endpoint utworzony: {api['path']}")

    # Uruchom serwer w tle
    from adapters.http_server_adapter import HttpServerAdapter

    server_thread = threading.Thread(target=HttpServerAdapter.run_server)
    server_thread.daemon = True
    server_thread.start()

    # Sprawdź API
    response = http_client.url('http://localhost:5000/api/hello').method('GET').execute()
    print(f"Odpowiedź z API: {response['message']}")


if __name__ == "__main__":
    main()