#!/usr/bin/env python3
from adapters import bash, HttpClientAdapter, python
from pipeline_engine import PipelineEngine

print("Running code.py")

# Przykład 1: Listowanie plików i filtrowanie przez Python
print("\n--- Przykład 1: Listowanie plików i filtrowanie ---")
result = bash.command('ls -la').execute()
filtered_result = python.code('''
result = [line for line in input_data.split("\\n") if ".py" in line]
''').execute(result)
print(filtered_result)

# Przykład 2: Pobranie danych z API i przetworzenie
print("\n--- Przykład 2: Pobranie danych z API ---")
try:
    # Używamy JSONPlaceholder, który jest publicznie dostępnym API do testów
    data = http_client.url('https://jsonplaceholder.typicode.com/todos/1').method('GET').execute()
    processed = python.code('''
    if isinstance(input_data, dict):
        result = input_data
    else:
        result = input_data
    ''').execute(data)
    print(processed)
except Exception as e:
    print(f"Błąd podczas wykonywania zapytania API: {e}")

# Przykład 3: Proste wykonanie polecenia bash
print("\n--- Przykład 3: Proste polecenie bash ---")
try:
    # Tworzymy prosty plik testowy
    bash.command('echo "Test content" > test_file.txt').execute()
    # Odczytujemy ten plik
    result = bash.command('cat test_file.txt').execute()
    print(f"Zawartość pliku: {result}")
except Exception as e:
    print(f"Błąd podczas wykonywania polecenia bash: {e}")