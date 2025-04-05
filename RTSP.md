
## 7. Dokumentacja nowych adapterów (docs/adapters/opencv_rtsp.md)

```markdown
# Adaptery OpenCV i RTSP

Adaptery do przetwarzania obrazu i obsługi strumieni wideo.

## Adapter OpenCV

Adapter OpenCV umożliwia przetwarzanie obrazów i detekcję obiektów za pomocą biblioteki OpenCV.

### Podstawowe operacje

#### Wczytywanie obrazu

```python
result = opencv.operation('read').execute('path/to/image.jpg')
```

Parametry:
- `output_path` - opcjonalna ścieżka do zapisania wczytanego obrazu

#### Przetwarzanie obrazu

```python
result = opencv.operation('process').operations([
    {'type': 'resize', 'width': 800, 'height': 600},
    {'type': 'convert_color', 'code': 6},  # BGR2GRAY
    {'type': 'blur', 'kernel_size': [5, 5]},
    {'type': 'threshold', 'value': 127, 'max_value': 255}
]).output_path('output.jpg').execute(image)
```

Dostępne operacje:
- `resize` - zmiana rozmiaru obrazu
- `blur` - rozmycie obrazu
- `threshold` - progowanie obrazu
- `canny` - detekcja krawędzi
- `convert_color` - konwersja przestrzeni kolorów
- `draw` - rysowanie na obrazie (prostokąty, tekst)

#### Detekcja obiektów

```python
# Detekcja twarzy za pomocą kaskad Haara
result = opencv.operation('detect').detection_method('haar').object_type('face').output_path('faces.jpg').execute(image)

# Detekcja za pomocą modeli DNN
result = opencv.operation('detect').detection_method('dnn').model_path('model.pb').config_path('config.pbtxt').execute(image)
```

Parametry:
- `detection_method` - metoda detekcji (`haar` lub `dnn`)
- `object_type` - typ obiektu dla metody Haar (`face`, `eye`, `smile`)
- `model_path` - ścieżka do modelu DNN
- `config_path` - ścieżka do konfiguracji modelu DNN
- `confidence_threshold` - próg pewności detekcji (domyślnie 0.5)

#### Przechwytywanie wideo

```python
# Przechwycenie klatki z kamery
result = opencv.operation('capture').source(0).output_path('frame.jpg').execute()

# Przechwycenie sekwencji klatek
result = opencv.operation('capture').source('video.mp4').capture_mode('sequence').frame_count(10).frame_interval(5).output_dir('frames/').execute()
```

Parametry:
- `source` - źródło wideo (0 dla kamery, ścieżka do pliku lub URL)
- `capture_mode` - tryb przechwytywania (`frame` lub `sequence`)
- `frame_count` - liczba klatek do przechwycenia
- `frame_interval` - odstęp między klatkami
- `process_frame` - czy przetwarzać klatkę (True/False)
- `operations` - operacje do przetworzenia klatki
- `save_frames` - czy zapisywać klatki (True/False)
- `output_dir` - katalog na zapisane klatki

## Adapter RTSP

Adapter RTSP umożliwia obsługę strumieni RTSP (Real Time Streaming Protocol).

### Podstawowe operacje

#### Nawiązywanie połączenia

```python
result = rtsp.operation('connect').url('rtsp://example.com/stream').stream_id('my_stream').execute()
```

Parametry:
- `url` - URL strumienia RTSP
- `stream_id` - identyfikator strumienia
- `connection_options` - opcje połączenia (np. `buffer_size`)

#### Pobieranie klatki

```python
result = rtsp.operation('get_frame').stream_id('my_stream').output_path('frame.jpg').execute()
```

Parametry:
- `stream_id` - identyfikator strumienia
- `process_frame` - czy przetwarzać klatkę (True/False)
- `operations` - operacje do przetworzenia klatki
- `output_path` - ścieżka do zapisania klatki

#### Nagrywanie strumienia

```python
result = rtsp.operation('record').stream_id('my_stream').duration(10).output_path('video.avi').execute()
```

Parametry:
- `stream_id` - identyfikator strumienia
- `duration` - czas nagrywania w sekundach
- `output_path` - ścieżka do zapisania nagrania

#### Zamykanie połączenia

```python
result = rtsp.operation('disconnect').stream_id('my_stream').execute()
```

Parametry:
- `stream_id` - identyfikator strumienia

## Integracja z systemem emulatorów drukarek

Adaptery OpenCV i RTSP można wykorzystać w systemie emulatorów drukarek do:

1. **Przetwarzania obrazów przed drukowaniem** - zmiana rozmiaru, konwersja kolorów, itp.
2. **Detekcji obiektów na obrazach** - identyfikacja elementów do druku
3. **Monitoringu procesu drukowania** - nagrywanie procesu druku za pomocą kamery
4. **Kontroli jakości wydruków** - porównywanie obrazu wydruku z oczekiwanym efektem

### Przykładowy pipeline

```yaml
pipelines:
  print-with-opencv:
    description: "Pipeline przetwarzania obrazu przed drukowaniem"
    steps:
      - adapter: rtsp
        methods:
          - name: operation
            value: "get_frame"
          - name: stream_id
            value: "printer_camera"
        output: camera_frame
      
      - adapter: opencv
        methods:
          - name: operation
            value: "process"
          - name: operations
            value:
              - type: "resize"
                width: 800
                height: 600
        input: ${results.camera_frame.frame}
        output: processed_image
      
      - adapter: zpl
        methods:
          - name: render_mode
            value: "labelary"
          - name: dpi
            value: 203
        input: ${results.processed_image.processed_image}
        output: label
```
```

Dzięki tym rozszerzeniom, system emulatorów drukarek zyskuje możliwość przetwarzania obrazów i obsługi strumieni wideo, co znacznie rozszerza jego funkcjonalność i możliwości zastosowania.