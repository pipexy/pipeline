# advanced_workflow.py
from adapters import bash, http_client, http_server, python, database, file
from message_queue_adapter import message_queue
from websocket_adapter import websocket
from ml_adapter import ml
import threading
import time
import os

# Utwórz potrzebne katalogi
os.makedirs('./data', exist_ok=True)
os.makedirs('./models', exist_ok=True)
os.makedirs('./reports', exist_ok=True)

# 1. Uruchomienie websocketa do monitorowania w czasie rzeczywistym
ws_server = websocket.port(9000).host('0.0.0.0').operation('serve').handler('''
# Handler do obsługi websocketów
import json

# Przetwórz dane wejściowe
if isinstance(data, str):
    try:
        data = json.loads(data)
    except:
        pass

# Jeśli to command, wykonaj odpowiednią operację
if isinstance(data, dict) and 'command' in data:
    command = data['command']

    if command == 'subscribe':
        # Zapisz klienta jako subskrybenta
        if not hasattr(socket, 'subscriptions'):
            socket.subscriptions = set()

        topic = data.get('topic', 'all')
        socket.subscriptions.add(topic)
        response = {'status': 'subscribed', 'topic': topic}

    elif command == 'unsubscribe':
        # Usuń subskrypcję
        if hasattr(socket, 'subscriptions'):
            topic = data.get('topic', 'all')
            socket.subscriptions.discard(topic)
            response = {'status': 'unsubscribed', 'topic': topic}
        else:
            response = {'status': 'error', 'message': 'No subscriptions'}

    elif command == 'stats':
        # Zwróć statystyki
        import psutil
        response = {
            'status': 'ok',
            'stats': {
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory().percent,
                'timestamp': time.time()
            }
        }

    else:
        response = {'status': 'error', 'message': f'Unknown command: {command}'}
else:
    response = {'status': 'error', 'message': 'Invalid message format'}
''').execute()

print(f"WebSocket server uruchomiony na porcie {ws_server['port']}")

# 2. Utworzenie API do analizy danych
data_analysis_api = http_server.path('/api/analyze-data').methods(['POST']).code('''
def request_handler(input_data):
   # Sprawdź czy mamy dane wejściowe
   if not input_data or not isinstance(input_data, dict):
       return {'error': 'Invalid input data'}, 400
   
   # Pobierz dane do analizy
   data_source = input_data.get('data_source')
   if not data_source:
       return {'error': 'No data source specified'}, 400
   
   try:
       # Przygotuj dane do analizy
       import pandas as pd
       import tempfile
       import os
       
       # Jeśli dane przesłano bezpośrednio w formacie JSON
       if 'data' in input_data and isinstance(input_data['data'], list):
           df = pd.DataFrame(input_data['data'])
       
       # Jeśli podano URL do danych
       elif data_source.startswith('http'):
           import requests
           response = requests.get(data_source)
           if not response.ok:
               return {'error': f'Failed to fetch data from {data_source}'}, 400
           
           # Zapisz dane do pliku tymczasowego
           with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp:
               temp.write(response.content)
               temp_path = temp.name
           
           # Odczytaj jako DataFrame
           df = pd.read_csv(temp_path)
           os.unlink(temp_path)  # Usuń plik tymczasowy
       
       # Jeśli podano lokalną ścieżkę
       elif os.path.exists(data_source):
           # Odczytaj plik w zależności od rozszerzenia
           if data_source.endswith('.csv'):
               df = pd.read_csv(data_source)
           elif data_source.endswith('.json'):
               df = pd.read_json(data_source)
           elif data_source.endswith('.xlsx') or data_source.endswith('.xls'):
               df = pd.read_excel(data_source)
           else:
               return {'error': 'Unsupported file format'}, 400
       else:
           return {'error': f'Data source not found: {data_source}'}, 404
       
       # Wykonaj analizę danych
       from ml_adapter import ml
       analysis_result = ml.operation('analyze').execute(df)
       
       # Opcjonalnie wykonaj predykcję jeśli podano model
       if 'model_path' in input_data and os.path.exists(input_data['model_path']):
           try:
               # Przygotuj dane do predykcji
               target_column = input_data.get('target_column')
               if target_column and target_column in df.columns:
                   X = df.drop(columns=[target_column])
               else:
                   X = df
               
               # Wykonaj predykcję
               prediction_result = ml.operation('predict').model_path(input_data['model_path']).execute(X)
               analysis_result['predictions'] = prediction_result
           except Exception as e:
               analysis_result['prediction_error'] = str(e)
       
       # Zapisz raport do pliku jeśli wymagane
       if input_data.get('save_report', False):
           import json
           import time
           
           report_path = f"./reports/analysis_{int(time.time())}.json"
           with open(report_path, 'w') as f:
               json.dump(analysis_result, f, indent=2)
           
           analysis_result['report_path'] = report_path
       
       # Powiadom subskrybentów websocketa
       try:
           import websocket as ws
           ws_client = ws.create_connection("ws://localhost:9000")
           ws_client.send(json.dumps({
               'topic': 'data_analysis',
               'event': 'analysis_complete',
               'data': {
                   'timestamp': time.time(),
                   'rows': len(df),
                   'columns': len(df.columns)
               }
           }))
           ws_client.close()
       except:
           pass
       
       return analysis_result
       
   except Exception as e:
       import traceback
       return {
           'error': 'Error processing data',
           'details': str(e),
           'traceback': traceback.format_exc()
       }, 500
''').execute()

print(f"API analizy danych dostępne pod: {data_analysis_api['path']}")

# 3. Pipeline do ETL z użyciem kolejki wiadomości i ML
def run_etl_pipeline():
   """Uruchomienie pipeline'u ETL z kolejką wiadomości."""
   # Utwórz pipeline do pobierania danych
   fetch_data = http_client.url('https://data.cityofnewyork.us/resource/h9gi-nx95.json').method('GET').params({
       '$limit': 1000,  # Ograniczenie do 1000 rekordów
       '$order': 'date DESC'
   }).execute()

   print(f"Pobrano {len(fetch_data)} rekordów danych")

   # Transformacja danych
   transform_result = python.code('''
   # Transformacja danych
   import pandas as pd
   import numpy as np
   from datetime import datetime
   
   # Konwersja do DataFrame
   df = pd.DataFrame(input_data)
   
   # Wybór i czyszczenie potrzebnych kolumn
   if 'longitude' in df.columns and 'latitude' in df.columns:
       df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
       df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
   
   # Konwersja dat
   date_columns = [col for col in df.columns if 'date' in col.lower()]
   for col in date_columns:
       try:
           df[col] = pd.to_datetime(df[col])
       except:
           pass
   
   # Wypełnienie brakujących wartości
   numeric_columns = df.select_dtypes(include=[np.number]).columns
   for col in numeric_columns:
       df[col] = df[col].fillna(df[col].median())
   
   # Usunięcie wierszy z brakującymi wartościami w kluczowych kolumnach
   if 'key_columns' in params:
       key_columns = params['key_columns']
       df = df.dropna(subset=key_columns)
   
   # Kodowanie zmiennych kategorycznych
   cat_columns = df.select_dtypes(include=['object']).columns
   for col in cat_columns:
       if df[col].nunique() < 50:  # Tylko dla kolumn z rozsądną liczbą kategorii
           dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
           df = pd.concat([df, dummies], axis=1)
   
   # Dodanie znacznika czasu przetwarzania
   df['processed_timestamp'] = datetime.now().isoformat()
   
   # Zapisz przetworzone dane do pliku CSV
   output_path = './data/processed_data.csv'
   df.to_csv(output_path, index=False)
   
   result = {
       'success': True,
       'rows_processed': len(df),
       'columns_processed': len(df.columns),
       'output_path': output_path,
       'column_stats': {
           col: {
               'type': str(df[col].dtype),
               'missing': int(df[col].isnull().sum()),
               'unique': int(df[col].nunique()) if df[col].dtype != 'float64' else None
           }
           for col in df.columns[:10]  # Ograniczenie do pierwszych 10 kolumn
       }
   }
   ''').execute(fetch_data, {'key_columns': ['date', 'time']})

   print(f"Przetransformowano dane: {transform_result['rows_processed']} wierszy")

   # Publikowanie wyniku do kolejki
   message_queue.type('redis').operation('publish').queue('etl_results').execute(transform_result)

   # Opcjonalnie, trening modelu ML
   train_model = ml.operation('train').model_type('random_forest_regressor').target_column('longitude').output_path('./models/geo_model.pkl').execute(transform_result['output_path'])

   print(f"Wytrenowano model: {train_model['model_type']}, dokładność: {train_model['test_score']:.4f}")

   # Ewaluacja modelu
   evaluate_model = ml.operation('evaluate').model_path('./models/geo_model.pkl').target_column('longitude').execute(transform_result['output_path'])

   print(f"Ewaluacja modelu - RMSE: {evaluate_model['metrics']['rmse']:.4f}")

   # Zapisanie raportu końcowego
   report_result = file.path('./reports/etl_report.json').operation('write').execute({
       'etl_timestamp': time.time(),
       'data_source': 'NYC Open Data',
       'records_processed': transform_result['rows_processed'],
       'model_performance': evaluate_model['metrics'],
       'model_path': train_model['model_path']
   })

   print(f"Zapisano raport ETL: {report_result['path']}")

   return {
       'success': True,
       'data_processed': transform_result,
       'model_trained': train_model,
       'model_evaluated': evaluate_model,
       'report': report_result
   }

# 4. API do uruchamiania pipeline'u ETL
etl_api = http_server.path('/api/run-etl').methods(['POST']).code('''
def request_handler(input_data):
   # Uruchom pipeline ETL w oddzielnym wątku
   import threading
   from advanced_workflow import run_etl_pipeline
   
   def etl_thread():
       try:
           result = run_etl_pipeline()
           
           # Powiadom przez websocket o zakończeniu
           import websocket as ws
           import json
           try:
               ws_client = ws.create_connection("ws://localhost:9000")
               ws_client.send(json.dumps({
                   'topic': 'etl_pipeline',
                   'event': 'completed',
                   'data': {
                       'timestamp': time.time(),
                       'success': True,
                       'records_processed': result['data_processed']['rows_processed']
                   }
               }))
               ws_client.close()
           except Exception as e:
               print(f"Error sending WebSocket notification: {e}")
       
       except Exception as e:
           import traceback
           error_details = {
               'error': str(e),
               'traceback': traceback.format_exc()
           }
           print(f"ETL Pipeline failed: {error_details}")
           
           # Powiadom o błędzie
           try:
               import websocket as ws
               import json
               ws_client = ws.create_connection("ws://localhost:9000")
               ws_client.send(json.dumps({
                   'topic': 'etl_pipeline',
                   'event': 'error',
                   'data': {
                       'timestamp': time.time(),
                       'error': str(e)
                   }
               }))
               ws_client.close()
           except:
               pass
   
   # Uruchom ETL w tle
   thread = threading.Thread(target=etl_thread)
   thread.daemon = True
   thread.start()
   
   return {
       'status': 'Pipeline ETL uruchomiony w tle',
       'message': 'Wyniki będą dostępne w katalogu ./reports'
   }
''').execute()

print(f"API uruchamiania ETL dostępne pod: {etl_api['path']}")

# 5. API do predykcji z wykorzystaniem wytrenowanego modelu
prediction_api = http_server.path('/api/predict').methods(['POST']).code('''
def request_handler(input_data):
   if not input_data or not isinstance(input_data, dict):
       return {'error': 'Invalid input data'}, 400
   
   model_path = input_data.get('model_path', './models/geo_model.pkl')
   
   # Sprawdź czy model istnieje
   import os
   if not os.path.exists(model_path):
       return {'error': f'Model not found: {model_path}'}, 404
   
   try:
       from ml_adapter import ml
       
       # Wykonaj predykcję
       prediction = ml.operation('predict').model_path(model_path).execute(input_data.get('data', {}))
       
       # Zapisz wynik predykcji do pliku jeśli wymagane
       if input_data.get('save_result', False):
           import json
           import time
           
           result_path = f"./reports/prediction_{int(time.time())}.json"
           with open(result_path, 'w') as f:
               json.dump(prediction, f, indent=2)
           
           prediction['result_path'] = result_path
       
       return prediction
   
   except Exception as e:
       import traceback
       return {
           'error': 'Error making prediction',
           'details': str(e),
           'traceback': traceback.format_exc()
       }, 500
''').execute()

print(f"API predykcji dostępne pod: {prediction_api['path']}")

# 6. Monitor dla wszystkich usług
status_api = http_server.path('/api/status').methods(['GET']).code('''
def request_handler(input_data):
   import psutil
   import os
   import time
   import glob
   
   # Zbierz informacje systemowe
   system_info = {
       'cpu_percent': psutil.cpu_percent(),
       'memory_percent': psutil.virtual_memory().percent,
       'disk_percent': psutil.disk_usage('/').percent,
       'timestamp': time.time()
   }
   
   # Sprawdź statusy API
   api_endpoints = [
       '/api/analyze-data',
       '/api/run-etl',
       '/api/predict',
       '/api/status'
   ]
   
   apis = [
       {
           'path': endpoint,
           'status': 'online'
       }
       for endpoint in api_endpoints
   ]
   
   # Sprawdź pliki w katalogach
   data_files = glob.glob('./data/*')
   model_files = glob.glob('./models/*')
   report_files = glob.glob('./reports/*')
   
   files_info = {
       'data_files': len(data_files),
       'model_files': len(model_files),
       'report_files': len(report_files),
       'total_size_mb': sum(os.path.getsize(f) for f in data_files + model_files + report_files) / (1024 * 1024)
   }
   
   # Zbierz wszystkie informacje
   return {
       'status': 'healthy',
       'system': system_info,
       'apis': apis,
       'files': files_info,
       'services': {
           'websocket': {'port': 9000, 'status': 'online'},
           'http_server': {'port': 5000, 'status': 'online'}
       }
   }
''').execute()

print(f"API statusu systemu dostępne pod: {status_api['path']}")

print("\nSystem uruchomiony i gotowy do użycia!")
print("Dostępne API:")
print("- POST /api/analyze-data  - Analiza danych")
print("- POST /api/run-etl       - Uruchomienie pipeline'u ETL")
print("- POST /api/predict       - Predykcja z użyciem modelu ML")
print("- GET  /api/status        - Status systemu")
print("\nWebSocket do monitorowania: ws://localhost:9000")

# Utrzymuj serwer uruchomiony
try:
   # Uruchom główny cykl serwera
   import time
   from flask import Flask
   app = HttpServerAdapter.get_app()

   # Uruchom serwer w głównym wątku
   app.run(host='0.0.0.0', port=5000)

except KeyboardInterrupt:
   print("\nZatrzymywanie systemu...")