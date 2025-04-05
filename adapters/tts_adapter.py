"""
Adapter do konwersji tekstu na mowę (Text-to-Speech).
Obsługuje różne języki i może korzystać z lokalnych oraz chmurowych silników TTS.
"""

import os
import tempfile
import json
import subprocess
from .base import BaseAdapter


class TTSAdapter(BaseAdapter):
    """Adapter do konwersji tekstu na mowę (Text-to-Speech)."""

    def _execute_self(self, input_data=None):
        # Pobierz tekst do konwersji
        text = input_data
        if isinstance(input_data, dict) and 'text' in input_data:
            text = input_data['text']

        # Sprawdź czy mamy tekst
        if not text:
            raise ValueError("No text provided for TTS conversion")

        # Pobierz parametry
        engine = self._params.get('engine', 'pyttsx3')  # Domyślnie lokalny silnik
        language = self._params.get('language', 'en')  # Domyślnie angielski
        voice = self._params.get('voice')  # Domyślnie brak (użyj domyślnego głosu)
        output_path = self._params.get('output_path')

        # Wybór metody konwersji
        if engine == 'pyttsx3':
            return self._tts_with_pyttsx3(text, language, voice, output_path)
        elif engine == 'gtts':
            return self._tts_with_gtts(text, language, output_path)
        elif engine == 'espeak':
            return self._tts_with_espeak(text, language, voice, output_path)
        elif engine == 'edge_tts':
            return self._tts_with_edge_tts(text, language, voice, output_path)
        else:
            raise ValueError(f"Unsupported TTS engine: {engine}")

    def _tts_with_pyttsx3(self, text, language, voice, output_path):
        """Konwersja tekstu na mowę za pomocą pyttsx3 (lokalny silnik)."""
        try:
            import pyttsx3
        except ImportError:
            raise ImportError("pyttsx3 is required. Install with 'pip install pyttsx3'")

        # Inicjalizacja silnika
        engine = pyttsx3.init()

        # Ustawienie właściwości
        if voice:
            voices = engine.getProperty('voices')
            for v in voices:
                if voice in v.id:
                    engine.setProperty('voice', v.id)
                    break

        # Ustawienie szybkości
        rate = self._params.get('rate')
        if rate:
            engine.setProperty('rate', rate)

        # Ustawienie głośności
        volume = self._params.get('volume')
        if volume:
            engine.setProperty('volume', volume)  # Głośność od 0.0 do 1.0

        # Jeśli podano output_path, zapisz do pliku
        if output_path:
            # Utwórz katalogi jeśli nie istnieją
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            engine.save_to_file(text, output_path)
            engine.runAndWait()
        else:
            # W przeciwnym razie wypowiedz tekst
            engine.say(text)
            engine.runAndWait()

        # Zwróć informacje o wykonaniu
        return {
            'success': True,
            'engine': 'pyttsx3',
            'text': text,
            'output_path': output_path,
            'language': language
        }

    def _tts_with_gtts(self, text, language, output_path):
        """Konwersja tekstu na mowę za pomocą Google Text-to-Speech (wymaga internetu)."""
        try:
            from gtts import gTTS
        except ImportError:
            raise ImportError("gTTS is required. Install with 'pip install gtts'")

        # Utwórz obiekt gTTS
        tts = gTTS(text=text, lang=language, slow=self._params.get('slow', False))

        # Jeśli podano output_path, zapisz do pliku
        if output_path:
            # Utwórz katalogi jeśli nie istnieją
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            tts.save(output_path)
        else:
            # W przeciwnym razie zapisz do pliku tymczasowego i odtwórz
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp:
                temp_path = temp.name

            tts.save(temp_path)

            # Odtwórz dźwięk
            self._play_audio(temp_path)

            # Usuń plik tymczasowy
            try:
                os.unlink(temp_path)
            except:
                pass

        # Zwróć informacje o wykonaniu
        return {
            'success': True,
            'engine': 'gtts',
            'text': text,
            'output_path': output_path,
            'language': language
        }

    def _tts_with_espeak(self, text, language, voice, output_path):
        """Konwersja tekstu na mowę za pomocą eSpeak (dobry wybór dla RPi)."""
        # Przygotuj polecenie
        cmd = ['espeak']

        # Dodaj język/głos
        if voice:
            cmd.extend(['-v', voice])
        elif language:
            cmd.extend(['-v', language])

        # Dodaj parametry
        speed = self._params.get('speed', 150)
        amplitude = self._params.get('amplitude', 100)
        pitch = self._params.get('pitch', 50)

        cmd.extend(['-s', str(speed), '-a', str(amplitude), '-p', str(pitch)])

        # Dodaj ścieżkę wyjściową
        if output_path:
            # Utwórz katalogi jeśli nie istnieją
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            cmd.extend(['-w', output_path])

        # Dodaj tekst
        cmd.append(text)

        # Wykonaj polecenie
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            # Zwróć informacje o wykonaniu
            return {
                'success': True,
                'engine': 'espeak',
                'text': text,
                'output_path': output_path,
                'language': language or voice,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"eSpeak error: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("eSpeak not found. Install with 'sudo apt-get install espeak'")

    def _tts_with_edge_tts(self, text, language, voice, output_path):
        """Konwersja tekstu na mowę za pomocą Microsoft Edge TTS (wymaga internetu)."""
        try:
            import edge_tts
            import asyncio
        except ImportError:
            raise ImportError("edge-tts is required. Install with 'pip install edge-tts'")

        # Jeśli nie podano głosu, wybierz domyślny dla języka
        if not voice:
            language_map = {
                'en': 'en-US-AriaNeural',
                'pl': 'pl-PL-AgnieszkaNeural',
                'de': 'de-DE-KatjaNeural',
                'fr': 'fr-FR-DeniseNeural',
                'es': 'es-ES-ElviraNeural',
                'it': 'it-IT-ElsaNeural',
                'ja': 'ja-JP-NanamiNeural',
                'ko': 'ko-KR-SunHiNeural',
                'zh': 'zh-CN-XiaoxiaoNeural',
                'ru': 'ru-RU-SvetlanaNeural'
            }
            voice = language_map.get(language, 'en-US-AriaNeural')

        # Funkcja asynchroniczna
        async def run_edge_tts():
            # Komunikujemy się z usługą Microsoft Edge TTS
            communicate = edge_tts.Communicate(text, voice)

            # Jeśli podano output_path, zapisz do pliku
            if output_path:
                # Utwórz katalogi jeśli nie istnieją
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                await communicate.save(output_path)
            else:
                # W przeciwnym razie zapisz do pliku tymczasowego i odtwórz
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp:
                    temp_path = temp.name

                await communicate.save(temp_path)

                # Odtwórz dźwięk
                self._play_audio(temp_path)

                # Usuń plik tymczasowy
                try:
                    os.unlink(temp_path)
                except:
                    pass

            return {
                'success': True,
                'engine': 'edge_tts',
                'text': text,
                'output_path': output_path,
                'voice': voice
            }

        # Wykonaj funkcję asynchroniczną
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_edge_tts())
        loop.close()

        return result

    def _play_audio(self, audio_file):
        """Odtwarza plik audio na różnych platformach."""
        import platform

        system = platform.system()

        try:
            if system == 'Windows':
                # Dla Windows
                os.startfile(audio_file)
            elif system == 'Darwin':
                # Dla macOS
                subprocess.run(['afplay', audio_file], check=True)
            else:
                # Dla Linux (w tym Raspberry Pi)
                # Sprawdź dostępność różnych odtwarzaczy
                players = ['mpg123', 'mpg321', 'aplay', 'mplayer']

                for player in players:
                    try:
                        subprocess.run(['which', player], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        # Odtwarzacz znaleziony
                        if player in ['mpg123', 'mpg321']:
                            subprocess.run([player, '-q', audio_file], check=True)
                        elif player == 'aplay':
                            subprocess.run([player, audio_file], check=True)
                        elif player == 'mplayer':
                            subprocess.run([player, '-really-quiet', audio_file], check=True)
                        return
                    except subprocess.CalledProcessError:
                        continue

                # Jeśli żaden odtwarzacz nie jest dostępny
                print(f"No audio player found. Cannot play {audio_file}")
        except Exception as e:
            print(f"Error playing audio: {e}")