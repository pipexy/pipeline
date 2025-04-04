#!/usr/bin/env python3

# Listowanie plików i filtrowanie
python cli.py --pipeline "bash.command('ls -la').python.code('result = [line for line in input_data.split(\"\\n\") if \".py\" in line]')"

# Przetwarzanie JSON
python cli.py --pipeline "python.code('result = [x*2 for x in input_data]')" --input "[1, 2, 3, 4]"

# Pobranie danych z API i zapisanie do pliku
python cli.py --pipeline "http.url('https://api.example.com/data').method('GET')" --output data.json