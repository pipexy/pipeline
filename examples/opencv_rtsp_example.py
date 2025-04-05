"""
Przykład użycia adapterów OpenCV i RTSP do przetwarzania strumienia wideo.
"""

from adapters import rtsp, opencv
import time
import os
import threading


def main():
    print("Przykład użycia adapterów OpenCV i RTSP")

    # 1. Połączenie ze strumieniem RTSP
    # Uwaga: Zmień URL na działający strumień RTSP
    rtsp_url = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4"

    stream_info = rtsp.url(rtsp_url).operation('connect').stream_id('demo_stream').execute()
    print(f"Połączono ze strumieniem: {stream_info['stream_id']}")
    print(f"Parametry strumienia: {stream_info['width']}x{stream_info['height']} @ {stream_info['fps']} FPS")

    # Utwórz katalog na wyniki
    output_dir = "./output/rtsp_frames"
    os.makedirs(output_dir, exist_ok=True)

    # 2. Pobieranie i przetwarzanie klatek
    try:
        # Pobierz 10 klatek
        for i in range(10):
            # Pobierz klatkę
            frame_result = rtsp.stream_id('demo_stream').operation('get_frame').output_path(
                f"{output_dir}/frame_original_{i:03d}.jpg").execute()

            print(f"Pobrano klatkę {i + 1}: {frame_result['width']}x{frame_result['height']}")

            # Przetwarzanie klatki z OpenCV
            processed_frame = opencv.operation('process').operations([
                # Konwersja na skalę szarości
                {'type': 'convert_color', 'code': 6},  # COLOR_BGR2GRAY
                # Detekcja krawędzi
                {'type': 'canny', 'threshold1': 100, 'threshold2': 200},
                # Dodanie tekstu
                {'type': 'draw', 'draw_type': 'text', 'text': f'Frame {i + 1}', 'position': (30, 30)}
            ]).output_path(f"{output_dir}/frame_processed_{i:03d}.jpg").execute(frame_result['frame'])

            print(f"Zapisano przetworzoną klatkę: {processed_frame['output_path']}")

            # Pauza między klatkami
            time.sleep(1)

        # 3. Detekcja twarzy na klatce
        # Pobierz klatkę
        frame_result = rtsp.stream_id('demo_stream').operation('get_frame').execute()

        # Detekcja twarzy
        faces_result = opencv.operation('detect').detection_method('haar').object_type('face').output_path(
            f"{output_dir}/faces_detected.jpg").execute(frame_result['frame'])

        print(f"Wykryto {faces_result['count']} twarzy")
        print(f"Zapisano wynik detekcji: {faces_result['output_path']}")

        # 4. Nagrywanie strumienia
        record_result = rtsp.stream_id('demo_stream').operation('record').duration(5).output_path(
            f"{output_dir}/recorded_stream.avi").execute()

        print(f"Nagrano {record_result['duration']} sekund wideo")
        print(f"Zapisano {record_result['frames_recorded']} klatek")
        print(f"Plik wyjściowy: {record_result['output_path']}")

    finally:
        # 5. Zamknięcie połączenia
        disconnect_result = rtsp.stream_id('demo_stream').operation('disconnect').execute()
        print(f"Zamknięto połączenie: {disconnect_result['message']}")


if __name__ == "__main__":
    main()