"""
Adapter do obsługi audio na Raspberry Pi.
Dostarcza zaawansowane funkcje audio dla Raspberry Pi z mikrofonem i głośnikiem.
"""

import os
import subprocess
import time
import json
import tempfile
from .base import BaseAdapter


class RpiAudioAdapter(BaseAdapter):
    """Adapter do obsługi audio na Raspberry Pi."""

    def _execute_self(self, input_data=None):
        # Pobierz operację do wykonania
        operation = self._params.get('operation', 'check_devices')

        # Wybór operacji
        if operation == 'check_devices':
            return self._check_audio_devices()
        elif operation == 'play_audio':
            return self._play_audio(input_data)
        elif operation == 'record_audio':
            return self._record_audio()
        elif operation == 'set_volume':
            return self._set_volume()
        elif operation == 'setup_audio':
            return self._setup_audio()
        elif operation == 'test_audio':
            return self._test_audio()
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _check_audio_devices(self):
        """Sprawdza dostępne urządzenia audio."""
        devices = {
            'microphones': [],
            'speakers': []
        }

        # Sprawdź urządzenia ALSA
        try:
            # Lista urządzeń wejściowych
            mic_result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
            if mic_result.returncode == 0:
                # Parsuj wynik
                for line in mic_result.stdout.splitlines():
                    if 'card' in line and 'device' in line:
                        devices['microphones'].append(line.strip())

            # Lista urządzeń wyjściowych
            spk_result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
            if spk_result.returncode == 0:
                # Parsuj wynik
                for line in spk_result.stdout.splitlines():
                    if 'card' in line and 'device' in line:
                        devices['speakers'].append(line.strip())
        except Exception as e:
            pass

        # Sprawdź urządzenia PulseAudio
        try:
            pulse_result = subprocess.run(['pactl', 'list'], capture_output=True, text=True)
            if pulse_result.returncode == 0:
                # Tutaj bardziej złożone parsowanie PulseAudio
                pass
        except:
            pass

        # Sprawdź aktualny stan
        try:
            # Aktualne urządzenie wejściowe
            amixer_result = subprocess.run(['amixer', 'sget', 'Capture'], capture_output=True, text=True)
            if amixer_result.returncode == 0:
                devices['current_mic'] = amixer_result.stdout

            # Aktualne urządzenie wyjściowe
            amixer_result = subprocess.run(['amixer', 'sget', 'Master'], capture_output=True, text=True)
            if amixer_result.returncode == 0:
                devices['current_speaker'] = amixer_result.stdout
        except:
            pass

        return {
            'success': True,
            'devices': devices,
            'is_raspberry_pi': self._is_raspberry_pi()
        }

    def _play_audio(self, input_data):
        """Odtwarza dźwięk na Raspberry Pi."""
        # Pobierz plik audio
        audio_file = None

        if isinstance(input_data, str):
            if os.path.exists(input_data):
                audio_file = input_data
        elif isinstance(input_data, dict) and 'audio_file' in input_data:
            if os.path.exists(input_data['audio_file']):
                audio_file = input_data['audio_file']

        if not audio_file:
            raise ValueError("No valid audio file provided")

        # Pobierz parametry
        volume = self._params.get('volume')
        device = self._params.get('device')

        # Ustaw głośność jeśli podano
        if volume is not None:
            try:
                subprocess.run(['amixer', 'set', 'Master', f'{volume}%'], check=True)
            except:
                pass

        # Odtwórz dźwięk
        try:
            if device:
                # Odtwarzanie na konkretnym urządzeniu
                if audio_file.endswith('.mp3'):
                    cmd = ['mpg123', '-a', device, audio_file]
                elif audio_file.endswith('.wav'):
                    cmd = ['aplay', '-D', device, audio_file]
                else:
                    # Domyślnie używaj aplay
                    cmd = ['aplay', '-D', device, audio_file]
            else:
                # Odtwarzanie na domyślnym urządzeniu
                if audio_file.endswith('.mp3'):
                    cmd = ['mpg123', audio_file]
                elif audio_file.endswith('.wav'):
                    cmd = ['aplay', audio_file]
                else:
                    # Domyślnie używaj aplay
                    cmd = ['aplay', audio_file]

            result = subprocess.run(cmd, capture_output=True, text=True)

            return {
                'success': result.returncode == 0,
                'audio_file': audio_file,
                'command': ' '.join(cmd),
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'audio_file': audio_file
            }

    def _record_audio(self):
        """Nagrywa dźwięk na Raspberry Pi."""
        # Pobierz parametry
        duration = self._params.get('duration', 5)  # Czas nagrywania w sekundach
        device = self._params.get('device')  # Urządzenie wejściowe
        output_path = self._params.get('output_path')  # Ścieżka do pliku wyjściowego

        # Jeśli nie podano ścieżki wyjściowej, użyj pliku tymczasowego
        if not output_path:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                output_path = tmp.name
        else:
            # Utwórz katalogi jeśli nie istnieją
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Nagraj dźwięk
        try:
            cmd = ['arecord']

            if device:
                cmd.extend(['-D', device])

            # Parametry nagrywania
            cmd.extend([
                '-f', 'S16_LE',  # Format
                '-c', '1',  # Mono
                '-r', '16000',  # Częstotliwość 16kHz
                '-d', str(duration),  # Czas trwania
               output_path           # Plik wyjściowy
           ])

           print(f"Nagrywam... (przez {duration} sekund)")
           result = subprocess.run(cmd, capture_output=True, text=True)
           print("Nagrywanie zakończone.")

           return {
               'success': result.returncode == 0,
               'audio_file': output_path,
               'duration': duration,
               'command': ' '.join(cmd),
               'stdout': result.stdout,
               'stderr': result.stderr
           }
       except Exception as e:
           return {
               'success': False,
               'error': str(e),
               'output_path': output_path
           }

   def _set_volume(self):
       """Ustawia głośność na Raspberry Pi."""
       # Pobierz parametry
       volume = self._params.get('volume')
       device = self._params.get('device', 'Master')

       if volume is None:
           raise ValueError("Volume parameter is required")

       # Ustaw głośność
       try:
           cmd = ['amixer', 'set', device, f'{volume}%']
           result = subprocess.run(cmd, capture_output=True, text=True)

           return {
               'success': result.returncode == 0,
               'volume': volume,
               'device': device,
               'command': ' '.join(cmd),
               'stdout': result.stdout,
               'stderr': result.stderr
           }
       except Exception as e:
           return {
               'success': False,
               'error': str(e),
               'device': device,
               'volume': volume
           }

   def _setup_audio(self):
       """Konfiguruje audio na Raspberry Pi."""
       # Pobierz parametry
       setup_type = self._params.get('setup_type', 'basic')

       if setup_type == 'basic':
           return self._setup_basic_audio()
       elif setup_type == 'usb_mic':
           return self._setup_usb_mic()
       elif setup_type == 'bluetooth':
           return self._setup_bluetooth_audio()
       elif setup_type == 'i2s':
           return self._setup_i2s_audio()
       else:
           raise ValueError(f"Unsupported setup type: {setup_type}")

   def _setup_basic_audio(self):
       """Podstawowa konfiguracja audio."""
       commands = [
           # Zainstaluj podstawowe pakiety audio
           'apt-get update',
           'apt-get install -y alsa-utils pulseaudio mpg123'
       ]

       results = []
       for cmd in commands:
           try:
               result = subprocess.run(cmd.split(), capture_output=True, text=True)
               results.append({
                   'command': cmd,
                   'success': result.returncode == 0,
                   'stdout': result.stdout,
                   'stderr': result.stderr
               })
           except Exception as e:
               results.append({
                   'command': cmd,
                   'success': False,
                   'error': str(e)
               })

       return {
           'success': all(r['success'] for r in results),
           'setup_type': 'basic',
           'results': results
       }

   def _setup_usb_mic(self):
       """Konfiguracja mikrofonów USB."""
       # Sprawdź czy mikrofon USB jest podłączony
       mic_check = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
       if 'USB' not in mic_check.stdout:
           return {
               'success': False,
               'error': 'No USB microphone detected',
               'setup_type': 'usb_mic'
           }

       # Utwórz/zmodyfikuj konfigurację ALSA
       asound_conf = """
pcm.!default {
 type asym
 capture.pcm "mic"
 playback.pcm "speaker"
}
pcm.mic {
 type plug
 slave {
   pcm "hw:1,0"
 }
}
pcm.speaker {
 type plug
 slave {
   pcm "hw:0,0"
 }
}
"""

       # Zapisz konfigurację
       try:
           with open('/etc/asound.conf', 'w') as f:
               f.write(asound_conf)
       except Exception as e:
           return {
               'success': False,
               'error': f"Failed to write ALSA configuration: {e}",
               'setup_type': 'usb_mic'
           }

       return {
           'success': True,
           'setup_type': 'usb_mic',
           'message': 'USB microphone configured successfully'
       }

   def _setup_bluetooth_audio(self):
       """Konfiguracja audio przez Bluetooth."""
       commands = [
           # Zainstaluj pakiety Bluetooth
           'apt-get update',
           'apt-get install -y bluetooth bluez bluez-tools pulseaudio-module-bluetooth'
       ]

       results = []
       for cmd in commands:
           try:
               result = subprocess.run(cmd.split(), capture_output=True, text=True)
               results.append({
                   'command': cmd,
                   'success': result.returncode == 0,
                   'stdout': result.stdout,
                   'stderr': result.stderr
               })
           except Exception as e:
               results.append({
                   'command': cmd,
                   'success': False,
                   'error': str(e)
               })

       # Restart usług
       try:
           subprocess.run(['systemctl', 'restart', 'bluetooth'], check=True)
           subprocess.run(['pulseaudio', '-k'], check=False)  # Zatrzymaj PulseAudio
           time.sleep(2)  # Poczekaj na restart
       except Exception as e:
           results.append({
               'command': 'restart services',
               'success': False,
               'error': str(e)
           })

       return {
           'success': all(r['success'] for r in results),
           'setup_type': 'bluetooth',
           'results': results,
           'next_steps': 'Pair your Bluetooth device using bluetoothctl'
       }

   def _setup_i2s_audio(self):
       """Konfiguracja audio przez I2S."""
       # To wymaga modyfikacji /boot/config.txt
       config_lines = [
           'dtparam=i2s=on',
           'dtoverlay=hifiberry-dac'  # Przykładowy overlay, może wymagać zmiany
       ]

       try:
           # Sprawdź czy linie już istnieją
           with open('/boot/config.txt', 'r') as f:
               existing_config = f.read()

           # Dodaj brakujące linie
           new_lines = []
           for line in config_lines:
               if line not in existing_config:
                   new_lines.append(line)

           if new_lines:
               with open('/boot/config.txt', 'a') as f:
                   f.write('\n# I2S Audio Configuration\n')
                   f.write('\n'.join(new_lines) + '\n')

           return {
               'success': True,
               'setup_type': 'i2s',
               'added_lines': new_lines,
               'message': 'I2S audio configured. Reboot required.'
           }
       except Exception as e:
           return {
               'success': False,
               'error': str(e),
               'setup_type': 'i2s'
           }

   def _test_audio(self):
       """Testuje audio na Raspberry Pi."""
       # Testuj wyjście audio
       output_test = self._test_audio_output()

       # Testuj wejście audio
       input_test = self._test_audio_input()

       return {
           'success': output_test['success'] and input_test['success'],
           'output_test': output_test,
           'input_test': input_test
       }

   def _test_audio_output(self):
       """Testuje wyjście audio (głośniki)."""
       # Utwórz tymczasowy plik testowy
       with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
           temp_file = tmp.name

       try:
           # Generuj sygnał testowy
           cmd = [
               'sox', '-n', temp_file,
               'synth', '3', 'sine', '440',  # 3-sekundowy dźwięk o częstotliwości 440 Hz
               'vol', '0.8'  # Głośność 80%
           ]

           subprocess.run(cmd, check=True, capture_output=True)

           # Odtwórz dźwięk
           play_result = self._play_audio(temp_file)

           return {
               'success': play_result['success'],
               'message': 'Audio output test completed',
               'details': play_result
           }
       except Exception as e:
           return {
               'success': False,
               'error': str(e),
               'message': 'Audio output test failed'
           }
       finally:
           # Usuń plik tymczasowy
           try:
               os.unlink(temp_file)
           except:
               pass

   def _test_audio_input(self):
       """Testuje wejście audio (mikrofon)."""
       # Nagraj krótki dźwięk
       record_result = self._record_audio()

       if not record_result['success']:
           return {
               'success': False,
               'message': 'Audio input test failed',
               'details': record_result
           }

       # Sprawdź czy plik ma odpowiedni rozmiar
       audio_file = record_result['audio_file']
       file_size = os.path.getsize(audio_file)

       try:
           # Usuń plik tymczasowy
           os.unlink(audio_file)
       except:
           pass

       return {
           'success': file_size > 1000,  # Sprawdź czy plik nie jest pusty
           'message': 'Audio input test completed',
           'file_size': file_size,
           'details': record_result
       }

   def _is_raspberry_pi(self):
       """Sprawdza czy urządzenie to Raspberry Pi."""
       try:
           with open('/proc/device-tree/model', 'r') as f:
               model = f.read()
               return 'Raspberry Pi' in model
       except:
           try:
               # Alternatywna metoda
               if os.path.exists('/sys/firmware/devicetree/base/model'):
                   with open('/sys/firmware/devicetree/base/model', 'r') as f:
                       model = f.read()
                       return 'Raspberry Pi' in model
           except:
               pass

       return False