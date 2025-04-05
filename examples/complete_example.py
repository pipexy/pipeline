# complete_example.py
from adapters_extended import bash, http_client, http_server, python, database, file, HttpServerAdapter
from pipeline_dsl import PipelineDSL
import threading
import time


# 1. Uruchomienie serwera mikroserwisów
def setup_microservices():
    # API użytkowników
    http_server.path('/api/users').methods(['GET']).code('''
    def request_handler(input_data):
        # W rzeczywistej aplikacji, dane pochodziłyby z bazy
        users = [
            {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
            {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'}
        ]
        return {'users': users}
    ''').execute()

    # API produktów
    http_server.path('/api/products').methods(['GET']).code('''
    def request_handler(input_data):
        products = [
            {'id': 101, 'name': 'Laptop', 'price': 999.99},
            {'id': 102, 'name': 'Smartphone', 'price': 499.99},
            {'id': 103, 'name': 'Headphones', 'price': 99.99}
        ]
        return {'products': products}
    ''').execute()

    # API zamówień z integracją produktów i użytkowników
    http_server.path('/api/orders').methods(['GET']).code('''
    def request_handler(input_data):
        import requests

        # Pobierz dane z innych mikroserwisów
        users_response = requests.get('http://127.0.0.1:5000/api/users')
        products_response = requests.get('http://127.0.0.1:5000/api/products')

        users = users_response.json().get('users', [])
        products = products_response.json().get('products', [])

        # Utwórz przykładowe zamówienia
        orders = [
            {
                'id': 1001,
                'user_id': 1,
                'user': next((u for u in users if u['id'] == 1), None),
                'product_ids': [101, 103],
                'products': [p for p in products if p['id'] in [101, 103]],
                'total': sum(p['price'] for p in products if p['id'] in [101, 103])
           },
           {
               'id': 1002,
               'user_id': 2,
               'user': next((u for u in users if u['id'] == 2), None),
               'product_ids': [102],
               'products': [p for p in products if p['id'] in [102]],
               'total': sum(p['price'] for p in products if p['id'] in [102])
           }
       ]
       
       return {'orders': orders, 'count': len(orders)}
   ''').execute()

   # Endpoint dla przetwarzania płatności
   http_server.path('/api/process-payment').methods(['POST']).code('''
   def request_handler(input_data):
       if not isinstance(input_data, dict):
           return {'error': 'Invalid payment data'}, 400
           
       order_id = input_data.get('order_id')
       amount = input_data.get('amount')
       card_info = input_data.get('card_info', {})
       
       if not order_id or not amount:
           return {'error': 'Missing required fields'}, 400
           
       # Symulacja przetwarzania płatności
       import random
       import time
       
       # Symuluj opóźnienie
       time.sleep(0.5)
       
       # 90% szans na sukces
       success = random.random() < 0.9
       
       if success:
           return {
               'success': True,
               'transaction_id': f'TX-{int(time.time())}-{order_id}',
               'order_id': order_id,
               'amount': amount,
               'status': 'completed'
           }
       else:
           return {
               'success': False,
               'order_id': order_id,
               'error': 'Payment processing failed',
               'status': 'failed'
           }, 400
   ''').execute()

   # Uruchom serwer w oddzielnym wątku
   server_thread = threading.Thread(target=HttpServerAdapter.run_server)
   server_thread.daemon = True
   server_thread.start()

   print("Mikroserwisy uruchomione na http://127.0.0.1:5000")
   return server_thread

# 2. Tworzenie pipeline'ów przetwarzania danych

def process_order_pipeline(order_id):
   """Pipeline przetwarzania zamówienia: pobranie danych, płatność, zapis do bazy."""

   # Pobranie danych zamówienia
   order_data = http_client.url(f'http://127.0.0.1:5000/api/orders').method('GET').python.code('''
   # Znajdź zamówienie o podanym ID
   order_id = params.get('order_id')
   
   if not isinstance(input_data, dict) or 'orders' not in input_data:
       result = {'error': 'Invalid response from orders API'}
       return result
       
   order = next((o for o in input_data['orders'] if o['id'] == order_id), None)
   
   if not order:
       result = {'error': f'Order {order_id} not found'}
       return result
   
   result = order
   ''').execute({"order_id": order_id})

   if 'error' in order_data:
       return {'error': order_data['error'], 'status': 'failed'}

   # Przetwarzanie płatności
   payment_result = http_client.url('http://127.0.0.1:5000/api/process-payment').method('POST').headers({
       'Content-Type': 'application/json'
   }).execute({
       'order_id': order_data['id'],
       'amount': order_data['total'],
       'card_info': {
           'number': '4111111111111111',  # Przykładowy numer karty testowej
           'exp_month': 12,
           'exp_year': 2025,
           'cvv': '123'
       }
   })

   if not payment_result.get('success', False):
       return {
           'error': 'Payment failed',
           'payment_details': payment_result,
           'status': 'payment_failed'
       }

   # Zapis do bazy danych (dla uproszczenia używamy SQLite)
   db_result = database.type('sqlite').connection('orders.db').query('''
   INSERT INTO orders (id, user_id, total, payment_id, status)
   VALUES (:id, :user_id, :total, :payment_id, 'completed')
   ''').execute({
       'id': order_data['id'],
       'user_id': order_data['user_id'],
       'total': order_data['total'],
       'payment_id': payment_result['transaction_id']
   })

   # Generowanie raportu zamówienia
   report = python.code('''
   from datetime import datetime
   
   # Połącz dane zamówienia i płatności
   result = {
       'order_id': input_data['id'],
       'user': input_data['user'],
       'products': input_data['products'],
       'total': input_data['total'],
       'payment': {
           'transaction_id': params.get('transaction_id'),
           'status': 'completed',
           'processed_at': datetime.now().isoformat()
       },
       'status': 'completed',
       'processed_at': datetime.now().isoformat()
   }
   ''').execute(order_data, {'transaction_id': payment_result['transaction_id']})

   # Zapisz raport do pliku
   file_result = file.path(f'./reports/order_{order_id}_{int(time.time())}.json').operation('write').execute(report)

   return {
       'success': True,
       'order_id': order_id,
       'payment_id': payment_result['transaction_id'],
       'status': 'completed',
       'report_file': file_result['path']
   }

# 3. Integracja z systemem monitoringu

def setup_monitoring():
   """Ustawienie monitoringu API i logów."""

   # Endpoint API do sprawdzania statusu
   status_endpoint = http_server.path('/api/status').methods(['GET']).code('''
   def request_handler(input_data):
       import psutil
       import datetime
       
       # Zbierz informacje o systemie
       cpu_percent = psutil.cpu_percent(interval=0.1)
       memory = psutil.virtual_memory()
       disk = psutil.disk_usage('/')
       
       # Sprawdź status usług
       services = [
           {'name': 'users-api', 'url': '/api/users', 'status': 'ok'},
           {'name': 'products-api', 'url': '/api/products', 'status': 'ok'},
           {'name': 'orders-api', 'url': '/api/orders', 'status': 'ok'},
           {'name': 'payment-api', 'url': '/api/process-payment', 'status': 'ok'}
       ]
       
       # Symulacja sprawdzania dostępności usług
       for service in services:
           try:
               if service['url'] == '/api/process-payment':
                   # Nie robimy rzeczywistego zapytania POST
                   continue
               
               response = requests.get(f"http://127.0.0.1:5000{service['url']}")
               service['status'] = 'ok' if response.status_code == 200 else 'error'
               service['response_time'] = response.elapsed.total_seconds()
           except Exception as e:
               service['status'] = 'error'
               service['error'] = str(e)
       
       return {
           'timestamp': datetime.datetime.now().isoformat(),
           'system': {
               'cpu_percent': cpu_percent,
               'memory_percent': memory.percent,
               'disk_percent': disk.percent
           },
           'services': services,
           'status': 'healthy' if all(s['status'] == 'ok' for s in services) else 'degraded'
       }
   ''').execute()

   # Logowanie dostępu do API
   access_log_middleware = http_server.code('''
   # Middleware do logowania dostępu
   def add_logging_middleware(app):
       @app.before_request
       def log_request():
           from flask import request
           import time
           request.start_time = time.time()
           
       @app.after_request
       def log_response(response):
           from flask import request
           import time
           import json
           
           # Oblicz czas trwania zapytania
           duration = time.time() - getattr(request, 'start_time', time.time())
           
           # Zapisz log do pliku
           log_entry = {
               'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
               'method': request.method,
               'path': request.path,
               'status_code': response.status_code,
               'duration_ms': round(duration * 1000, 2),
               'ip': request.remote_addr,
               'user_agent': request.user_agent.string
           }
           
           with open('./logs/api_access.log', 'a') as f:
               f.write(json.dumps(log_entry) + '\\n')
               
           return response
           
   # Get the Flask app and add middleware
   app = HttpServerAdapter.get_app()
   add_logging_middleware(app)
   
   result = {'status': 'Logging middleware added to Flask app'}
   ''').execute()

   print("System monitoringu skonfigurowany")

   return {'status_endpoint': status_endpoint, 'logging': access_log_middleware}

# 4. Główna funkcja uruchamiająca cały system

def main():
   """Uruchomienie całego systemu."""
   # Utwórz potrzebne katalogi
   import os
   os.makedirs('./reports', exist_ok=True)
   os.makedirs('./logs', exist_ok=True)

   # Utwórz bazę danych SQLite
   db_init = database.type('sqlite').connection('orders.db').query('''
   CREATE TABLE IF NOT EXISTS orders (
       id INTEGER PRIMARY KEY,
       user_id INTEGER,
       total REAL,
       payment_id TEXT,
       status TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   ''').execute()

   # Uruchom mikroserwisy
   server_thread = setup_microservices()

   # Skonfiguruj monitoring
   monitoring = setup_monitoring()

   # Poczekaj na uruchomienie serwera
   print("Czekanie na uruchomienie serwera...")
   time.sleep(2)

   # Przetwórz przykładowe zamówienie
   print("\nPrzetwarzanie przykładowego zamówienia...")
   order_result = process_order_pipeline(1001)
   print(f"Wynik przetwarzania zamówienia: {order_result}")

   # Sprawdź status systemu
   print("\nSprawdzanie statusu systemu...")
   status = http_client.url('http://127.0.0.1:5000/api/status').method('GET').execute()
   print(f"Status systemu: {status['status']}")
   print(f"Obciążenie CPU: {status['system']['cpu_percent']}%")
   print(f"Dostępne usługi: {', '.join(s['name'] for s in status['services'])}")

   # Udostępnij API do przetwarzania zamówień
   print("\nUruchamianie API do przetwarzania zamówień...")
   order_api = http_server.path('/api/process-order/{order_id}').methods(['POST']).code(f'''
   def request_handler(input_data):
       from flask import request
       import re
       
       # Wyciągnij order_id z ścieżki URL
       match = re.search(r'/api/process-order/([0-9]+)', request.path)
       if not match:
           return {{'error': 'Invalid order ID'}}, 400
           
       order_id = int(match.group(1))
       
       # Przetworz zamówienie za pomocą pipeline'a
       # W rzeczywistej aplikacji, uruchomilibyśmy to asynchronicznie
       # z użyciem kolejki zadań, ale dla uproszczenia robimy to synchronicznie
       import json
       
       # Zapisz dane wejściowe z requestu
       with open(f'./logs/order_request_{{order_id}}.json', 'w') as f:
           json.dump(input_data, f, indent=2)
       
       # Przetwórz zamówienie
       result = process_order_pipeline(order_id)
       
       # Zwróć status
       if 'error' in result:
           return result, 400
           
       return result
   ''').execute()

   print(f"API do przetwarzania zamówień dostępne pod: {order_api['path']}")
   print("\nSystem uruchomiony i gotowy do użycia!")
   print("Dostępne API:")
   print("- GET  /api/users            - Lista użytkowników")
   print("- GET  /api/products         - Lista produktów")
   print("- GET  /api/orders           - Lista zamówień")
   print("- POST /api/process-payment  - Przetwarzanie płatności")
   print("- GET  /api/status           - Status systemu")
   print("- POST /api/process-order/ID - Przetwarzanie zamówienia")

   # Utrzymuj serwer uruchomiony
   try:
       while True:
           time.sleep(1)
   except KeyboardInterrupt:
       print("\nZatrzymywanie systemu...")

if __name__ == "__main__":
   main()