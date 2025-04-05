"""
Adapter do konwersji mowy na tekst (Speech-to-Text).
Obsługuje różne języki i może korzystać z lokalnych oraz chmurowych silników STT.
"""

import os
import tempfile
import json
import subprocess
import time
from .base import BaseAdapter


class STTAdapter(BaseAdapter):
    """Adapter do konwersji mowy na tekst (Speech-to-Text)."""

    def _execute_self(self, input_data=None):
        # Pobierz parametry
        engine = self._params.get('engine', 'vosk')  # Domyślnie Vosk (działa offline)
        language = self._params.get('language', 'en')  # Domyślnie angielski
        audio_file = self._params.get('audio_file')
        duration = self._params.get('duration', 5)  # Czas nagrywania w sekundach

        # Pobierz źródło dźwięku
        if input_data and isinstance(input_data, str) and os.path.exists(input_data):
            # Plik audio podany jako input_data
            audio_file = input_data
        elif input_data and isinstance(input_data, dict) and 'audio_file' in input_data:
            # Plik audio podany w słowniku
            audio_file = input_data['audio_file']

        # Jeśli nie podano pliku audio, nagrywaj z mikrofonu
        if not audio_file:
            audio_file = self._record_audio(duration)
            # Flaga że plik jest tymczasowy
            is_temp_file = True
        else:
            is_temp_file = False

        try:
            # Wybór silnika STT
            if engine == 'vosk':
                result = self._stt_with_vosk(audio_file, language)
            elif engine == 'whisper':
                result = self._stt_with_whisper(audio_file, language)
            elif engine == 'google':
                result = self._stt_with_google(audio_file, language)
            elif engine == 'deepspeech':
                result = self._stt_with_deepspeech(audio_file, language)
            else:
                raise ValueError(f"Unsupported STT engine: {engine}")

            # Dodaj informację o pliku audio
            result['audio_file'] = audio_file

            return result
        finally:
            # Usuń plik tymczasowy jeśli nagrywaliśmy
            if is_temp_file:
                try:
                    os.unlink(audio_file)
                except:
                    pass

    def _record_audio(self, duration):
        """Nagrywa dźwięk z mikrofonu przez określony czas."""
        try:
            import pyaudio
            import wave
        except ImportError:
            raise ImportError("pyaudio is required. Install with 'pip install pyaudio'")

        # Parametry nagrywania
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024

        # Utwórz plik tymczasowy
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file_path = temp_file.name
        temp_file.close()

        # Inicjalizacja PyAudio
        audio = pyaudio.PyAudio()

        # Otwórz strumień
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)

        print(f"Nagrywam... (przez {duration} sekund)")

        frames = []

        # Nagrywaj przez określony czas
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("Nagrywanie zakończone.")

        # Zatrzymaj strumień
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Zapisz nagranie do pliku WAV
        with wave.open(temp_file_path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        return temp_file_path

    def _stt_with_vosk(self, audio_file, language):
        """Konwersja mowy na tekst za pomocą Vosk (działa offline)."""
        try:
            from vosk import Model, KaldiRecognizer, SetLogLevel
            import wave
        except ImportError:
            raise ImportError("vosk is required. Install with 'pip install vosk'")

        # Wycisz logi Vosk
        SetLogLevel(-1)

        # Ścieżka do modelu
        model_path = self._params.get('model_path')

        # Jeśli nie podano ścieżki, użyj domyślnej dla języka
        if not model_path:
            model_dir = self._params.get('model_dir', './models/vosk')
            model_path = os.path.join(model_dir, f'vosk-model-small-{language}')

        # Sprawdź czy model istnieje
        if not os.path.exists(model_path):
            raise ValueError(f"Vosk model not found: {model_path}. Download from https://alphacephei.com/vosk/models")

        # Załaduj model
        model = Model(model_path)

        # Otwórz plik audio
        with wave.open(audio_file, 'rb') as wf:
            # Sprawdź parametry
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != 'NONE':
                raise ValueError("Audio file must be WAV format mono PCM.")

            # Utwórz recognizer
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)

            # Przetwarzaj plik
            results = []

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break

                if rec.AcceptWaveform(data):
                    part_result = json.loads(rec.Result())
                    results.append(part_result)

            # Dodaj ostatni wynik
            part_result = json.loads(rec.FinalResult())
            results.append(part_result)

        # Połącz wyniki
        text = ' '.join(r.get('text', '') for r in results if 'text' in r)

        return {
            'success': True,
            'engine': 'vosk',
            'text': text,
            'language': language,
            'results': results
        }

    def _stt_with_whisper(self, audio_file, language):
        """Konwersja mowy na tekst za pomocą OpenAI Whisper (działa offline)."""
        try:
            import whisper
        except ImportError:
            raise ImportError("whisper is required. Install with 'pip install openai-whisper'")

        # Model Whisper
        model_size = self._params.get('model_size', 'small')

        # Załaduj model
        model = whisper.load_model(model_size)

        # Transkrybuj
        result = model.transcribe(
            audio_file,
            language=language if language != 'en' else None,
            task="transcribe" if self._params.get('translate', False) else None
        )

        return {
            'success': True,
            'engine': 'whisper',
            'text': result['text'],
            'language': language,
            'segments': result['segments']
        }

    def _stt_with_google(self, audio_file, language):
        """Konwersja mowy na tekst za pomocą Google Speech Recognition (wymaga internetu)."""
        try:
            import speech_recognition as sr
        except ImportError:
            raise ImportError("speech_recognition is required. Install with 'pip install SpeechRecognition'")

        # Inicjalizacja recognizer
        r = sr.Recognizer()

        # Wczytaj plik audio
        with sr.AudioFile(audio_file) as source:
            # Dostosuj dla szumu otoczenia
            r.adjust_for_ambient_noise(source)
            # Wczytaj dane audio
            audio_data = r.record(source)

        # Rozpoznawaj mowę
        try:
            text = r.recognize_google(audio_data, language=language)

            return {
                'success': True,
                'engine': 'google',
                'text': text,
                'language': language
            }
        except sr.UnknownValueError:
            return {
                'success': False,
                'engine': 'google',
                'error': 'Google Speech Recognition could not understand audio',
                'language': language,
                'text': ''
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'engine': 'google',
                'error': f'Could not request results from Google Speech Recognition service: {e}',
                'language': language,
                'text': ''
            }

    def _stt_with_deepspeech(self, audio_file, language):
        """Konwersja mowy na tekst za pomocą Mozilla DeepSpeech (działa offline)."""
        try:
            import deepspeech
        except ImportError:
            raise ImportError("deepspeech is required. Install with 'pip install deepspeech'")

        # Ścieżka do modelu
        model_path = self._params.get('model_path')

        # Jeśli nie podano ścieżki, użyj domyślnej
        if not model_path:
            model_dir = self._params.get('model_dir', './models/deepspeech')
            model_path = os.path.join(model_dir, 'deepspeech-0.9.3-models.pbmm')

        # Sprawdź czy model istnieje
        if not os.path.exists(model_path):
            raise ValueError(
                f"DeepSpeech model not found: {model_path}. Download from https://github.com/mozilla/DeepSpeech/releases")

        # Załaduj model
        model = deepspeech.Model(model_path)

        # Załaduj plik scorera jeśli podano
        scorer_path = self._params.get('scorer_path')
        if scorer_path and os.path.exists(scorer_path):
            model.enableExternalScorer(scorer_path)

        # Wczytaj plik audio
        import wave
        import numpy as np

        with wave.open(audio_file, 'rb') as w:
            rate = w.getframerate()
            frames = w.readframes(w.getnframes())
            buffer = np.frombuffer(frames, dtype=np.int16)

        # Rozpoznawanie mowy
        text = model.stt(buffer)

        return {
            'success': True,
            'engine': 'deepspeech',
            'text': text,
            'language': language  # DeepSpeech głównie obsługuje angielski
        }