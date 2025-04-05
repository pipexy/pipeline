# Przykład notacji kropkowej
"""
dot_notation_example.py
"""

"""
Przykład użycia notacji kropkowej w DSL.
"""

from core.pipeline_engine import PipelineEngine


def main():
    """Przykład użycia notacji kropkowej."""
    # Przykład 1: Łańcuch przetwarzania pliku tekstowego
    result1 = PipelineEngine.execute_from_dot_notation(
        "file.path('./data/sample.txt').operation('read')"
        ".python.code('result = len(input_data.split(\"\\n\"))')"
    )

    print(f"Liczba linii w pliku: {result1}")

    # Przykład 2: Pipeline przetwarzania danych
    result2 = PipelineEngine.execute_from_dot_notation(
        "http_client.url('https://jsonplaceholder.typicode.com/users').method('GET')"
        ".python.code('result = [user[\"name\"] for user in input_data]')"
        ".file.path('./output/users.txt').operation('write')"
    )

    print(f"Lista użytkowników zapisana do: {result2['path']}")

    # Przykład 3: Obsługa warunkowa
    data = {'value': 42}

    result3 = PipelineEngine.execute_from_dot_notation(
        "conditional.condition('input_data[\"value\"] > 10')"
        ".if_true(lambda x: {'result': 'Value is greater than 10'})"
        ".if_false(lambda x: {'result': 'Value is less than or equal to 10'})",
        data
    )

    print(f"Wynik warunkowy: {result3['result']}")

    # Przykład 4: Generowanie raportu
    result4 = PipelineEngine.execute_from_dot_notation(
        "python.code('''"
        "import datetime\n"
        "result = {\n"
        "    'report_name': 'System Status',\n"
        "    'generated_at': datetime.datetime.now().isoformat(),\n"
        "    'status': 'ok'\n"
        "}"
        "''')"
        ".file.path('./output/report_${timestamp}.json').operation('write')"
    )

    print(f"Raport wygenerowany: {result4['path']}")


if __name__ == "__main__":
    main()