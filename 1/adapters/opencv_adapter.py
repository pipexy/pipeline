"""
Adapter do przetwarzania obrazów i wideo za pomocą OpenCV.
"""

import os
import tempfile
import numpy as np
import json
from .base import BaseAdapter


class OpenCVAdapter(BaseAdapter):
    """Adapter do przetwarzania obrazów i wideo za pomocą OpenCV."""

    def _execute_self(self, input_data=None):
        try:
            import cv2
        except ImportError:
            raise ImportError("OpenCV is required. Install with 'pip install opencv-python'")

        # Ustal operację do wykonania
        operation = self._params.get('operation', 'read')

        # Obsługa różnych operacji
        if operation == 'read':
            return self._read_image(input_data, cv2)
        elif operation == 'process':
            return self._process_image(input_data, cv2)
        elif operation == 'detect':
            return self._detect_objects(input_data, cv2)
        elif operation == 'capture':
            return self._capture_video(cv2)
        else:
            raise ValueError(f"Unsupported OpenCV operation: {operation}")

    def _read_image(self, input_data, cv2):
        """Wczytuje obraz z pliku lub danych binarnych."""
        # Sprawdź źródło obrazu
        if isinstance(input_data, str) and os.path.exists(input_data):
            # Wczytaj z pliku
            image = cv2.imread(input_data)
        elif isinstance(input_data, bytes):
            # Wczytaj z danych binarnych
            nparr = np.frombuffer(input_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(input_data, dict) and 'path' in input_data:
            # Wczytaj z pliku podanego w dict
            image = cv2.imread(input_data['path'])
        elif isinstance(input_data, dict) and 'data' in input_data:
            # Wczytaj z danych binarnych podanych w dict
            nparr = np.frombuffer(input_data['data'], np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            raise ValueError("Invalid input data for image reading")

        if image is None:
            raise ValueError("Failed to read image")

        # Opcjonalnie zapisz obraz
        output_path = self._params.get('output_path')
        if output_path:
            # Utwórz katalogi jeśli nie istnieją
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            cv2.imwrite(output_path, image)

        # Zwróć wynik
        return {
            'image': image,
            'height': image.shape[0],
            'width': image.shape[1],
            'channels': image.shape[2] if len(image.shape) > 2 else 1,
            'output_path': output_path
        }

    def _process_image(self, input_data, cv2):
        """Przetwarza obraz za pomocą OpenCV."""
        # Pobierz obraz wejściowy
        if isinstance(input_data, dict) and 'image' in input_data:
            image = input_data['image']
        elif isinstance(input_data, np.ndarray):
            image = input_data
        else:
            # Spróbuj wczytać obraz
            image_data = self._read_image(input_data, cv2)
            image = image_data['image']

        # Wykonaj operacje przetwarzania
        operations = self._params.get('operations', [])
        processed_image = image.copy()

        for op in operations:
            op_type = op.get('type')

            if op_type == 'resize':
                width = op.get('width', int(processed_image.shape[1] * op.get('scale', 1.0)))
                height = op.get('height', int(processed_image.shape[0] * op.get('scale', 1.0)))
                processed_image = cv2.resize(processed_image, (width, height), interpolation=cv2.INTER_AREA)

            elif op_type == 'blur':
                kernel_size = op.get('kernel_size', (5, 5))
                processed_image = cv2.GaussianBlur(processed_image, kernel_size, 0)

            elif op_type == 'threshold':
                threshold_value = op.get('value', 127)
                max_value = op.get('max_value', 255)
                threshold_type = op.get('threshold_type', cv2.THRESH_BINARY)
                _, processed_image = cv2.threshold(processed_image, threshold_value, max_value, threshold_type)

            elif op_type == 'canny':
                threshold1 = op.get('threshold1', 100)
                threshold2 = op.get('threshold2', 200)
                processed_image = cv2.Canny(processed_image, threshold1, threshold2)

            elif op_type == 'convert_color':
                color_code = op.get('code', cv2.COLOR_BGR2GRAY)
                processed_image = cv2.cvtColor(processed_image, color_code)

            elif op_type == 'draw':
                draw_type = op.get('draw_type')
                if draw_type == 'rectangle':
                    pt1 = tuple(op.get('pt1', (0, 0)))
                    pt2 = tuple(op.get('pt2', (100, 100)))
                    color = tuple(op.get('color', (0, 255, 0)))
                    thickness = op.get('thickness', 2)
                    processed_image = cv2.rectangle(processed_image, pt1, pt2, color, thickness)
                elif draw_type == 'text':
                    text = op.get('text', 'Text')
                    position = tuple(op.get('position', (10, 30)))
                    font = op.get('font', cv2.FONT_HERSHEY_SIMPLEX)
                    font_scale = op.get('font_scale', 1.0)
                    color = tuple(op.get('color', (0, 255, 0)))
                    thickness = op.get('thickness', 2)
                    processed_image = cv2.putText(processed_image, text, position, font, font_scale, color, thickness)

        # Opcjonalnie zapisz wynik
        output_path = self._params.get('output_path')
        if output_path:
            # Utwórz katalogi jeśli nie istnieją
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            cv2.imwrite(output_path, processed_image)

        return {
            'original_image': image,
            'processed_image': processed_image,
            'height': processed_image.shape[0],
            'width': processed_image.shape[1],
            'channels': processed_image.shape[2] if len(processed_image.shape) > 2 else 1,
            'output_path': output_path
        }

    def _detect_objects(self, input_data, cv2):
        """Wykrywa obiekty na obrazie za pomocą kaskad Haara lub DNN."""
        # Pobierz obraz wejściowy
        if isinstance(input_data, dict) and 'image' in input_data:
            image = input_data['image']
        elif isinstance(input_data, np.ndarray):
            image = input_data
        else:
            # Spróbuj wczytać obraz
            image_data = self._read_image(input_data, cv2)
            image = image_data['image']

        # Pobierz metodę detekcji
        detection_method = self._params.get('detection_method', 'haar')

        if detection_method == 'haar':
            return self._detect_with_haar(image, cv2)
        elif detection_method == 'dnn':
            return self._detect_with_dnn(image, cv2)
        else:
            raise ValueError(f"Unsupported detection method: {detection_method}")

    def _detect_with_haar(self, image, cv2):
        """Wykrywa obiekty za pomocą kaskad Haara."""
        # Pobierz typ obiektu do wykrycia
        object_type = self._params.get('object_type', 'face')

        # Konwersja do skali szarości
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Wybierz odpowiednią kaskadę
        cascade_path = self._params.get('cascade_path')
        if not cascade_path:
            # Użyj wbudowanych kaskad
            if object_type == 'face':
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            elif object_type == 'eye':
                cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            elif object_type == 'smile':
                cascade_path = cv2.data.haarcascades + 'haarcascade_smile.xml'
            else:
                raise ValueError(f"Unsupported object type: {object_type}")

        # Załaduj kaskadę
        cascade = cv2.CascadeClassifier(cascade_path)

        # Wykonaj detekcję
        scale_factor = self._params.get('scale_factor', 1.1)
        min_neighbors = self._params.get('min_neighbors', 5)
        min_size = tuple(self._params.get('min_size', (30, 30)))

        objects = cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size
        )

        # Narysuj wykryte obiekty
        output_image = image.copy()

        for (x, y, w, h) in objects:
            cv2.rectangle(output_image, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Opcjonalnie zapisz wynik
        output_path = self._params.get('output_path')
        if output_path:
            # Utwórz katalogi jeśli nie istnieją
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            cv2.imwrite(output_path, output_image)

        # Lista wykrytych obiektów
        detected_objects = []
        for (x, y, w, h) in objects:
            detected_objects.append({
                'x': int(x),
                'y': int(y),
                'width': int(w),
                'height': int(h),
                'confidence': 1.0  # Haar nie daje dokładnych wartości pewności
            })

        return {
            'input_image': image,
            'output_image': output_image,
            'objects': detected_objects,
            'object_type': object_type,
            'count': len(detected_objects),
            'output_path': output_path
        }

    def _detect_with_dnn(self, image, cv2):
        """Wykrywa obiekty za pomocą modeli DNN."""
        # Pobierz model i konfigurację
        model_path = self._params.get('model_path')
        config_path = self._params.get('config_path')

        if not model_path or not config_path:
            raise ValueError("Model path and config path are required for DNN detection")

        # Załaduj model
        net = cv2.dnn.readNetFromCaffe(config_path, model_path)

        # Przygotuj obraz
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )

        # Detekcja obiektów
        net.setInput(blob)
        detections = net.forward()

        # Narysuj wykryte obiekty
        output_image = image.copy()

        # Lista wykrytych obiektów
        detected_objects = []

        # Próg pewności
        confidence_threshold = self._params.get('confidence_threshold', 0.5)

        # Przetwarzanie wyników detekcji
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > confidence_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # Narysuj prostokąt
                cv2.rectangle(output_image, (startX, startY), (endX, endY), (0, 255, 0), 2)

                # Dodaj etykietę z pewnością
                text = f"{confidence * 100:.2f}%"
                y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.putText(output_image, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

                # Zapisz wykryty obiekt
                detected_objects.append({
                    'x': int(startX),
                    'y': int(startY),
                    'width': int(endX - startX),
                    'height': int(endY - startY),
                    'confidence': float(confidence)
                })

        # Opcjonalnie zapisz wynik
        output_path = self._params.get('output_path')
        if output_path:
            # Utwórz katalogi jeśli nie istnieją
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            cv2.imwrite(output_path, output_image)

        return {
            'input_image': image,
            'output_image': output_image,
            'objects': detected_objects,
            'count': len(detected_objects),
            'output_path': output_path
        }

    def _capture_video(self, cv2):
        """Przechwytuje klatkę lub sekwencję klatek z kamery lub strumienia wideo."""
        # Pobierz źródło wideo
        source = self._params.get('source', 0)  # Domyślnie kamera 0

        # Tryb przechwytywania
        capture_mode = self._params.get('capture_mode', 'frame')  # 'frame' lub 'sequence'

        # Liczba klatek do przechwycenia
        frame_count = self._params.get('frame_count', 1)

        # Odstęp między klatkami
        frame_interval = self._params.get('frame_interval', 1)

        try:
            # Otwórz źródło wideo
            cap = cv2.VideoCapture(source)

            # Sprawdź czy udało się otworzyć
            if not cap.isOpened():
                raise ValueError(f"Failed to open video source: {source}")

            # Inicjalizacja wyniku
            captured_frames = []

            # Przechwytywanie klatek
            frame_index = 0
            frame_counter = 0

            while frame_counter < frame_count:
                # Wczytaj klatkę
                ret, frame = cap.read()

                # Sprawdź czy udało się wczytać
                if not ret:
                    break

                # Sprawdź czy to klatka do przechwycenia
                if frame_index % frame_interval == 0:
                    # Przetwarzanie klatki
                    if self._params.get('process_frame', False):
                        operations = self._params.get('operations', [])
                        processed_frame = frame.copy()

                        for op in operations:
                            op_type = op.get('type')

                            if op_type == 'resize':
                                width = op.get('width', int(processed_frame.shape[1] * op.get('scale', 1.0)))
                                height = op.get('height', int(processed_frame.shape[0] * op.get('scale', 1.0)))
                                processed_frame = cv2.resize(processed_frame, (width, height),
                                                             interpolation=cv2.INTER_AREA)

                            elif op_type == 'convert_color':
                                color_code = op.get('code', cv2.COLOR_BGR2GRAY)
                                processed_frame = cv2.cvtColor(processed_frame, color_code)
                    else:
                        processed_frame = frame

                    # Dodaj klatkę do wyniku
                    captured_frames.append({
                        'frame': processed_frame,
                        'index': frame_index
                    })

                    # Opcjonalnie zapisz klatkę
                    if self._params.get('save_frames', False):
                        output_dir = self._params.get('output_dir')
                        if output_dir:
                            # Utwórz katalogi jeśli nie istnieją
                            os.makedirs(output_dir, exist_ok=True)

                            # Zapisz klatkę
                            frame_path = os.path.join(output_dir, f"frame_{frame_index:04d}.png")
                            cv2.imwrite(frame_path, processed_frame)

                    frame_counter += 1

                frame_index += 1

                # Sprawdź czy tryb to pojedyncza klatka
                if capture_mode == 'frame' and frame_counter >= 1:
                    break

            # Zamknij źródło wideo
            cap.release()

            # Zwróć wynik
            if capture_mode == 'frame':
                if not captured_frames:
                    raise ValueError("Failed to capture frame")

                result = {
                    'frame': captured_frames[0]['frame'],
                    'height': captured_frames[0]['frame'].shape[0],
                    'width': captured_frames[0]['frame'].shape[1],
                    'channels': captured_frames[0]['frame'].shape[2] if len(
                        captured_frames[0]['frame'].shape) > 2 else 1
                }

                # Opcjonalnie zapisz klatkę
                output_path = self._params.get('output_path')
                if output_path:
                    # Utwórz katalogi jeśli nie istnieją
                    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                    cv2.imwrite(output_path, result['frame'])
                    result['output_path'] = output_path

                return result
            else:
                return {
                    'frames': [{'image': frame['frame'], 'index': frame['index']} for frame in captured_frames],
                    'count': len(captured_frames),
                    'output_dir': self._params.get('output_dir')
                }

        except Exception as e:
            raise RuntimeError(f"Error capturing video: {e}")