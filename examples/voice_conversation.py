"""
Przykład implementacji konwersacji głosowej z użyciem TTS i STT.
Umożliwia interakcję głosową w różnych językach.
"""

from adapters import tts, stt, rpi_audio
import time
import os
import json

# Domyślne ustawienia
DEFAULT_LANGUAGE = 'pl'  # Możesz zmienić na inny język
DEFAULT_TTS_ENGINE = 'espeak'  # Lokalny silnik dobry dla RPi
DEFAULT_STT_ENGINE = 'vosk'  # Lokalny silnik dobry dla RPi

# Obsługiwane języki (kod, nazwa, głos TTS)
SUPPORTED_LANGUAGES = {
    'pl': {'name': 'Polski', 'voice': 'pl'},
    'en': {'name': 'English', 'voice': 'en-us'},
    'de': {'name': 'Deutsch', 'voice': 'de'},
    'fr': {'name': 'Français', 'voice': 'fr'},
    'es': {'name': 'Español', 'voice': 'es'}
}


class VoiceConversation:
    """Klasa do konwersacji głosowej."""

    def __init__(self, language=DEFAULT_LANGUAGE, tts_engine=DEFAULT_TTS_ENGINE, stt_engine=DEFAULT_STT_ENGINE):
        """Inicjalizacja konwersacji głosowej."""
        self.language = language
        self.tts_engine = tts_engine
        self.stt_engine = stt_engine

        # Sprawdź czy to Raspberry Pi
        self.is_rpi = self._check_if_rpi()

        # Przygotuj katalogi na pliki audio
        os.makedirs('./output/audio', exist_ok=True)

        # Przygotuj katalog na logi
        os.makedirs('./logs', exist_ok=True)

        # Plik logu
        self.log_file = f'./logs/conversation_{int(time.time())}.log'

        # Odpowiedzi w różnych językach
        self.responses = {
            'pl': {
                'welcome': 'Witaj! Jak mogę Ci pomóc?',
                'not_understand': 'Przepraszam, nie zrozumiałem. Czy możesz powtórzyć?',
                'processing': 'Przetwarzam...',
                'goodbye': 'Do widzenia! Miłego dnia!',
                'select_language': 'Wybierz język:'
            },
            'en': {
                'welcome': 'Hello! How can I help you?',
                'not_understand': 'I\'m sorry, I didn\'t understand. Can you repeat?',
                'processing': 'Processing...',
                'goodbye': 'Goodbye! Have a nice day!',
                'select_language': 'Select language:'
            },
            'de': {
                'welcome': 'Hallo! Wie kann ich Ihnen helfen?',
                'not_understand': 'Es tut mir leid, ich habe nicht verstanden. Können Sie bitte wiederholen?',
                'processing': 'Verarbeitung...',
                'goodbye': 'Auf Wiedersehen! Schönen Tag noch!',
                'select_language': 'Sprache auswählen:'
            },
            'fr': {
                'welcome': 'Bonjour! Comment puis-je vous aider?',
                'not_understand': 'Désolé, je n\'ai pas compris. Pouvez-vous répéter?',
                'processing': 'Traitement en cours...',
                'goodbye': 'Au revoir! Bonne journée!',
                'select_language': 'Sélectionnez la langue:'
            },
            'es': {
                'welcome': '¡Hola! ¿Cómo puedo ayudarte?',
                'not_understand': 'Lo siento, no entendí. ¿Puedes repetir?',
                'processing': 'Procesando...',
                'goodbye': '¡Adiós! ¡Que tengas un buen día!',
                'select_language': 'Selecciona el idioma:'
            }
        }

        # Zaloguj inicjalizację
        self.log({
            'event': 'init',
            'language': language,
            'tts_engine': tts_engine,
            'stt_engine': stt_engine,
            'is_rpi': self.is_rpi
        })

    def _check_if_rpi(self):
        """Sprawdza czy urządzenie to Raspberry Pi."""
        if self.is_rpi is not None:
            return self.is_rpi

        try:
            result = rpi_audio.operation('check_devices').execute()
            return result.get('is_raspberry_pi', False)
        except:
            # Jeśli nie możemy sprawdzić, zakładamy że nie jest to RPi
            return False

    def log(self, data):
        """Zapisuje informacje do logu."""
        log_entry = {
            'timestamp': time.time(),
            'data': data
        }

        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except:
            pass

    def speak(self, text):
        """Wypowiada tekst i zapisuje do logu."""
        print(f"🔊 {text}")

        # Zaloguj wypowiedź
        self.log({
            'event': 'speak',
            'text': text,
            'language': self.language,
            'engine': self.tts_engine
        })

        # Ustaw głos dla języka
        voice = SUPPORTED_LANGUAGES.get(self.language, {}).get('voice')

        # Wypowiedz tekst
        response = tts.engine(self.tts_engine).language(self.language).voice(voice).execute(text)

        return response

    def listen(self, duration=5):
        """Słucha i rozpoznaje mowę."""
        print(f"🎤 Listening... ({duration}s)")

        # Zaloguj nasłuchiwanie
        self.log({
            'event': 'listen',
            'duration': duration,
            'language': self.language,
            'engine': self.stt_engine
        })

        # Jeśli to Raspberry Pi, użyj adaptera RPi do nagrywania
        if self.is_rpi:
            # Nagraj dźwięk
            audio_result = rpi_audio.operation('record_audio').duration(duration).execute()

            if not audio_result['success']:
                self.log({
                    'event': 'error',
                    'message': 'Failed to record audio',
                    'details': audio_result
                })
                return None

            audio_file = audio_result['audio_file']
        else:
            # Użyj adaptera STT do nagrywania
            audio_file = None  # STT sam nagra

        # Rozpoznaj mowę
        result = stt.engine(self.stt_engine).language(self.language).execute(audio_file)

        # Zaloguj wynik
        self.log({
            'event': 'stt_result',
            'success': result.get('success', False),
            'text': result.get('text', ''),
            'engine': self.stt_engine
        })

        if not result.get('success', False) or not result.get('text'):
            return None

        print(f"🎤 Recognized: {result['text']}")
        return result['text']

    def select_language(self):
        """Pozwala użytkownikowi wybrać język."""
        prompt = self.responses[self.language]['select_language']
        self.speak(prompt)

        # Wyświetl dostępne języki
        for code, info in SUPPORTED_LANGUAGES.items():
            self.speak(f"{code}: {info['name']}")

        # Nasłuchuj wyboru
        choice = self.listen(5)

        if choice and choice.lower() in SUPPORTED_LANGUAGES:
            self.language = choice.lower()
            self.speak(self.responses[self.language]['welcome'])
            return True

        return False

    def process_command(self, command):
        """Przetwarza komendę głosową."""
        # Proste komendy do demonstracji
        command = command.lower()

        if 'language' in command or 'język' in command or 'sprache' in command or 'idioma' in command or 'langue' in command:
            return self.select_language()

        if 'goodbye' in command or 'do widzenia' in command or 'auf wiedersehen' in command or 'adiós' in command or 'au revoir' in command:
            self.speak(self.responses[self.language]['goodbye'])
            return False

        # Tutaj możesz dodać więcej komend

        # Domyślna odpowiedź - echo
        self.speak(command)
        return True

    def run(self):
        """Uruchamia konwersację głosową."""
        # Powitanie
        self.speak(self.responses[self.language]['welcome'])

        running = True
        while running:
            # Nasłuchuj komendy
            command = self.listen()

            if command:
                # Przetwórz komendę
                running = self.process_command(command)
            else:
                # Nie zrozumiano
                self.speak(self.responses[self.language]['not_understand'])


def main():
    """Funkcja główna."""
    print("=== Voice Conversation Example ===")
    print("Language: Polish (pl)")
    print("TTS Engine: eSpeak")
    print("STT Engine: Vosk")
    print("=================================")

    # Utwórz obiekt konwersacji
    conversation = VoiceConversation()

    # Uruchom konwersację
    conversation.run()


if __name__ == "__main__":
    main()