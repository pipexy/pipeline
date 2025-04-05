# examples.py
from adapters import bash, http_client, http_server, python, database, file, HttpServerAdapter

# Przykład 1: Serwer HTTP przetwarzający dane z Pythona
server_config = http_server.path('/api/hello').methods(['GET', 'POST']).code('''
def request_handler(input_data):
    import datetime
    result = {
        'message': 'Hello World!',
        'timestamp': datetime.datetime.now().isoformat(),
        'input': input_data
    }
    return result
''').execute()

print(f"Utworzono endpoint: {server_config['path']}, metody: {server_config['methods']}")

# Uruchomienie serwera (w tle, w oddzielnym wątku)
import threading

server_thread = threading.Thread(target=HttpServerAdapter.run_server)
server_thread.daemon = True
server_thread.start()
print("Serwer HTTP uruchomiony na http://127.0.0.1:5000")

# Przykład 2: Łańcuch przetwarzania: HTTP → Python → Plik
# Pobierz dane z API, przetwórz je i zapisz do pliku
result = http_client.url('http://127.0.0.1:5000/api/hello').method('GET').python.code('''
# Przetwarzanie danych wejściowych
if isinstance(input_data, dict):
    input_data['processed'] = True
    input_data['count'] = len(str(input_data))
result = input_data
''').file.path('./output/processed_data.json').operation('write').execute()

print(f"Zapisano wynik do pliku: {result['path']}")

# Przykład 3: Parsowanie logu, filtrowanie i zapis do bazy danych
log_process = bash.command('cat /var/log/syslog | grep ERROR').python.code('''
# Przetwarzanie logów
lines = input_data.split('\\n')
parsed_logs = []
for line in lines:
    if line.strip():
        parts = line.split(' ', 3)
        if len(parts) >= 4:
            parsed_logs.append({
                'date': parts[0],
                'time': parts[1],
                'host': parts[2],
                'message': parts[3]
            })
result = parsed_logs
''').database.type('sqlite').connection('logs.db').query('''
INSERT INTO error_logs (date, time, host, message) 
VALUES (:date, :time, :host, :message)
''').execute()

print(f"Zapisano {log_process['affected_rows']} wierszy do bazy danych")

# Przykład 4: Pobranie danych z bazy, przetworzenie i zwrócenie przez API
api_endpoint = http_server.path('/api/logs').methods('GET').code('''
def request_handler(input_data):
    # Połącz z bazą danych
    import sqlite3
    conn = sqlite3.connect('logs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Pobierz logi z ostatniej godziny
    cursor.execute('''
SELECT * FROM
error_logs
WHERE
datetime(date | | ' ' | | time) > datetime('now', '-1 hour')
ORDER
BY
date
DESC, time
DESC
''')

# Konwertuj wyniki na słowniki
logs = [dict(row) for row in cursor.fetchall()]

# Zamknij połączenie
conn.close()

return {'logs': logs, 'count': len(logs)}
''').execute()

print(f"Utworzono endpoint API dla logów: {api_endpoint['path']}")

# Testowe zapytanie do naszego API
logs_response = http_client.url('http://127.0.0.1:5000/api/logs').method('GET').execute()
print(f"Pobrano {logs_response['count']} logów z API")