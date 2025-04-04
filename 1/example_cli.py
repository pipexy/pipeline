from adapters import bash, php, python, http, node
from pipeline_engine import PipelineEngine

# Przykład 1: Listowanie plików i filtrowanie przez Python
result = bash.command('ls -la').execute()
filtered_result = python.code('''
result = [line for line in input_data.split("\\n") if ".py" in line]
''').execute(result)
print(filtered_result)

# Przykład 2: Pobranie danych z API i przetworzenie
data = http.url('https://api.example.com/data').method('GET').execute()
processed = python.code('''
result = [item for item in input_data if item["active"] == True]
''').execute(data)
print(processed)

# Przykład 3: Wykonanie pipeline'a w notacji kropkowej
result = PipelineEngine.execute_from_dot_notation(
    'bash.command("cat data.json").python.code("result = [x for x in input_data if x[\'value\'] > 100]")'
)
print(result)