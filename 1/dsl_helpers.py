# dsl_helpers.py
from adapters import bash, php, python, http, node


def pipeline(*steps):
    """Łączy kroki w jeden pipeline i wykonuje go."""
    result = None
    for step in steps:
        result = step.execute(result)
    return result


def parallel(*steps):
    """Wykonuje kroki równolegle i zwraca listę wyników."""
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(step.execute) for step in steps]
        return [future.result() for future in futures]

# Przykłady użycia:
# result = pipeline(
#     bash.command('ls -la'),
#     python.code('result = input_data.split("\\n")')
# )
#
# results = parallel(
#     http.url('https://api.example.com/data1'),
#     http.url('https://api.example.com/data2')
# )