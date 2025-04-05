# advanced_examples.py
from adapters_extended import bash, http_client, http_server, python, database, file

# Przykład 1: ETL pipeline - pobierz dane, przekształć, załaduj do bazy
etl_result = http_client.url('https://api.example.com/data').method('GET').python.code('''
# Transformacja danych
transformed_data = []
for item in input_data:
    transformed_data.append({
        'id': item.get('id'),
        'name': item.get('name', '').upper(),  # Konwersja nazwy na wielkie litery
        'value': float(item.get('value', 0)) * 1.1,  # Zwiększenie wartości o 10%
        'processed_date': datetime.datetime.now().isoformat()
    })
result = transformed_data
''').database.type('sqlite').connection('data.db').query('''
INSERT INTO processed_items (id, name, value, processed_date) 
VALUES (:id, :name, :value, :processed_date)
''').python.code('''
# Raport z przetwarzania
result = {
    'processed_count': len(input_data.get('affected_rows', 0)),
    'status': 'success',
    'timestamp': datetime.datetime.now().isoformat()
}
''').file.path('./output/etl_report.json').operation('write').execute()

print(f"ETL zakończony, raport zapisany do: {etl_result['path']}")

# Przykład 2: Mikrousługa - serwer API z bazą danych
api_service = http_server.path('/api/users').methods(['GET']).code('''
def request_handler(input_data):
    # Połącz z bazą danych
    import sqlite3
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Pobierz użytkowników
    cursor.execute('SELECT * FROM users')
    users = [dict(row) for row in cursor.fetchall()]

    # Zamknij połączenie
    conn.close()

    return {'users': users, 'count': len(users)}
''').execute()

user_creation = http_server.path('/api/users').methods(['POST']).code('''
def request_handler(input_data):
    # Walidacja danych
    if not isinstance(input_data, dict) or not input_data.get('name'):
        return {'error': 'Invalid user data'}, 400

    # Połącz z bazą danych
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Dodaj użytkownika
    cursor.execute(
        'INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)',
        (input_data.get('name'), input_data.get('email'), datetime.datetime.now().isoformat())
    )

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {'id': user_id, 'success': True}
''').execute()

print(f"Utworzono API dla użytkowników: GET i POST {api_service['path']}")

# Przykład 3: Automatyczne monitorowanie logów i powiadomienia
monitoring_pipeline = bash.command('tail -f /var/log/syslog').python.code('''
import re
import time
from threading import Thread

# Wzorzec do wykrywania błędów
error_pattern = re.compile(r'ERROR|CRITICAL|FATAL', re.IGNORECASE)

# Funkcja nasłuchująca
def monitor_stream(input_stream):
    for line in input_stream.splitlines():
        if error_pattern.search(line):
            # Znaleziono błąd, wywołaj webhook
            requests.post(
                'https://hooks.slack.com/services/XXX/YYY/ZZZ',
                json={'text': f'Error detected: {line}'}
            )

            # Zapisz błąd do bazy
            conn = sqlite3.connect('monitoring.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO errors (message, detected_at) VALUES (?, ?)',
                (line, datetime.datetime.now().isoformat())
            )
            conn.commit()
            conn.close()

    # Uruchom w tle
    thread = Thread(target=monitor_stream, args=(input_data,))
    thread.daemon = True
    thread.start()

    result = {'status': 'Monitoring started', 'pattern': 'ERROR|CRITICAL|FATAL'}
''').execute()

print(f"Uruchomiono monitoring logów: {monitoring_pipeline['status']}")