"""
Adapter do obsługi strumieni RTSP (Real Time Streaming Protocol).
"""

import os
import tempfile
import time
import threading
import json
from .base import BaseAdapter


class RtspAdapter(BaseAdapter):
    """Adapter do obsługi strumieni RTSP."""

    # Słownik przechowujący aktywne strumienie
    _active_streams = {}

    def _execute_self(self, input_data=None):
        try:
            import cv2
        except ImportError:
            raise ImportError("OpenCV is required for RTSP adapter. Install with 'pip install opencv-python'")

        # Ustal operację do wykonania
        operation = self._params.get('operation', 'connect')

        # Obsługa różnych operacji
        if operation == 'connect':
            return self._connect_stream(cv2)
        elif operation == 'disconnect':
            return self._disconnect_stream()
        elif operation == 'get_frame':
            return self._get_frame(cv2)
        elif operation == 'record':
            return self._record_stream(cv2)
        else:
            raise ValueError(f"Unsupported RTSP operation: {operation}")

    def _connect_stream(self, cv2):
        """Nawiązuje połączenie ze strumieniem RTSP."""
        # Pobierz URL strumienia
        url = self._params.get('url')
        if not url:
            raise ValueError("RTSP URL is required")

        # Identyfikator strumienia
        stream_id = self._params.get('stream_id', f"stream_{int(time.time())}")

        # Opcje połączenia
        connection_options = self._params.get('connection_options', {})

        # Numer bufora
        buffer_size = connection_options.get('buffer_size', 10)

        # Utworzenie VideoCapture
        cap = cv2.VideoCapture(url)

        # Sprawdź czy udało się połączyć
        if not cap.isOpened():
            raise ValueError(f"Failed to connect to RTSP stream: {url}")

        # Pobierz informacje o strumieniu
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Zapisz strumień w słowniku
        RtspAdapter._active_streams[stream_id] = {
            'capture': cap,
            'url': url,
            'width': width,
            'height': height,
            'fps': fps,
            'last_frame': None,
            'buffer': [],
            'buffer_size': buffer_size,
            'running': True
        }

        # Uruchom wątek odczytujący klatki
        stream_thread = threading.Thread(
            target=self._stream_reader_thread,
            args=(stream_id, cap, buffer_size)
        )
        stream_thread.daemon = True
        stream_thread.start()

        # Zwróć informacje o strumieniu
        return {
            'stream_id': stream_id,
            'url': url,
            'width': width,
            'height': height,
            'fps': fps,
            'connected': True
        }

    def _stream_reader_thread(self, stream_id, cap, buffer_size):
        """Wątek odczytujący klatki ze strumienia."""
        while RtspAdapter._active_streams.get(stream_id, {}).get('running', False):
            # Wczytaj klatkę
            ret, frame = cap.read()

            # Sprawdź czy udało się wczytać
            if not ret:
                time.sleep(0.1)
                continue

            # Zapisz ostatnią klatkę
            RtspAdapter._active_streams[stream_id]['last_frame'] = frame

            # Dodaj klatkę do bufora
            if buffer_size > 0:
                buffer = RtspAdapter._active_streams[stream_id]['buffer']
                buffer.append(frame)

                # Usuń nadmiarowe klatki
                while len(buffer) > buffer_size:
                    buffer.pop(0)

            # Mała pauza
            time.sleep(0.01)

    def _disconnect_stream(self):
        """Zamyka połączenie ze strumieniem RTSP."""
        # Pobierz identyfikator strumienia
        stream_id = self._params.get('stream_id')
        if not stream_id:
            raise ValueError("Stream ID is required for disconnect operation")

        # Sprawdź czy strumień istnieje
        if stream_id not in RtspAdapter._active_streams:
            return {'success': False, 'error': f"Stream {stream_id} not found"}

        # Zatrzymaj wątek
        RtspAdapter._active_streams[stream_id]['running'] = False

        # Zamknij strumień
        RtspAdapter._active_streams[stream_id]['capture'].release()

        # Usuń strumień ze słownika
        del RtspAdapter._active_streams[stream_id]

        return {
            'success': True,
            'stream_id': stream_id,
            'message': f"Stream {stream_id} disconnected"
        }

    def _get_frame(self, cv2):
        """Pobiera klatkę ze strumienia RTSP."""
        # Pobierz identyfikator strumienia
        stream_id = self._params.get('stream_id')
        if not stream_id:
            raise ValueError("Stream ID is required for get_frame operation")

        # Sprawdź czy strumień istnieje
        if stream_id not in RtspAdapter._active_streams:
            raise ValueError(f"Stream {stream_id} not found")

        # Pobierz ostatnią klatkę
        frame = RtspAdapter._active_streams[stream_id]['last_frame']

        if frame is None:
            raise ValueError(f"No frames available for stream {stream_id}")

        # Opcjonalne przetwarzanie klatki
        if self._params.get('process_frame', False):
            # Użyj adaptera OpenCV do przetworzenia klatki
            from .opencv_adapter import OpenCVAdapter

            opencv_adapter = OpenCVAdapter('opencv')

            # Przygotuj parametry
            operations = self._params.get('operations', [])

            # Utwórz parametry dla adaptera OpenCV
            opencv_params = {
                'operation': 'process',
                'operations': operations,
                'output_path': self._params.get('output_path')
            }

            # Skopiuj wszystkie parametry do adaptera
            for key, value in opencv_params.items():
                opencv_adapter._params[key] = value

            # Wykonaj przetwarzanie
            result = opencv_adapter._execute_self(frame)

            # Pobierz przetworzony obraz
            frame = result['processed_image']

        # Opcjonalnie zapisz klatkę
        output_path = self._params.get('output_path')
        if output_path:
            # Utwórz katalogi jeśli nie istnieją
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            cv2.imwrite(output_path, frame)

        # Zwróć wynik
        return {
            'frame': frame,
            'stream_id': stream_id,
            'timestamp': time.time(),
            'width': frame.shape[1],
            'height': frame.shape[0],
            'output_path': output_path
        }

    def _record_stream(self, cv2):
        """Nagrywa strumień RTSP do pliku."""
        # Pobierz identyfikator strumienia
        stream_id = self._params.get('stream_id')
        if not stream_id:
            raise ValueError("Stream ID is required for record operation")

        # Sprawdź czy strumień istnieje
        if stream_id not in RtspAdapter._active_streams:
            raise ValueError(f"Stream {stream_id} not found")

        # Pobierz parametry nagrywania
        output_path = self._params.get('output_path')
        if not output_path:
            raise ValueError("Output path is required for record operation")

        # Utwórz katalogi jeśli nie istnieją
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Czas nagrywania w sekundach
        duration = self._params.get('duration', 10)

        # Pobierz parametry strumienia
        stream_info = RtspAdapter._active_streams[stream_id]
        width = stream_info['width']
        height = stream_info['height']
        fps = stream_info['fps']

        # Utwórz obiekt VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Nagraj strumień
        start_time = time.time()
        frames_recorded = 0

        while time.time() - start_time < duration:
            # Pobierz klatkę
            frame = stream_info['last_frame']

            if frame is not None:
                # Zapisz klatkę
                out.write(frame)
                frames_recorded += 1

            # Mała pauza
            time.sleep(1 / fps)

        # Zamknij VideoWriter
        out.release()

        return {
            'success': True,
            'stream_id': stream_id,
            'output_path': output_path,
            'duration': duration,
            'frames_recorded': frames_recorded,
            'fps': fps
        }