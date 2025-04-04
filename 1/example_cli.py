from adapters_extended import bash, http_client, python

# Przykład 1: Listowanie plików i filtrowanie przez Python
# result = bash.command('ls -la').execute()
# filtered_result = python.code('''
# result = [line for line in input_data.split("\\n") if ".py" in line]
# ''').execute(result)
# print(filtered_result)

# Przykład 2: Pobranie danych z API i przetworzenie - zakomentowane aby uniknąć błędu
# data = http_client.url('https://jsonplaceholder.typicode.com/todos').method('GET').execute()
# processed = python.code('''
# result = [item for item in input_data if item["completed"] == True][:5]  # Limit to 5 items
# ''').execute(data)
# print(processed)

# Przykład 3: Wykonanie pipeline'a w notacji kropkowej - zakomentowane do czasu poprawienia
from pipeline_engine import PipelineEngine
result = PipelineEngine.execute_from_dot_notation(
    'bash.command("echo {\\"value\\": 150, \\"name\\": \\"test\\"} > data.json && cat data.json")'
)
print(result)