# Plik inicjalizacyjny z rejestracją adapterów
"""
Moduł inicjalizacyjny adapterów.
Importuje i rejestruje wszystkie dostępne adaptery.
"""


# Dodaj na początku pliku importy nowych adapterów
from .tts_adapter import TTSAdapter
from .stt_adapter import STTAdapter
from .rpi_audio_adapter import RpiAudioAdapter
from .opencv_adapter import OpenCVAdapter
from .rtsp_adapter import RtspAdapter


from .base import BaseAdapter

# Importowanie adapterów
from .bash_adapter import BashAdapter
from .http_client_adapter import HttpClientAdapter
from .http_server_adapter import HttpServerAdapter
from .file_adapter import FileAdapter
from .python_adapter import PythonAdapter
from .database_adapter import DatabaseAdapter
from .ml_adapter import MLAdapter
from .message_queue_adapter import MessageQueueAdapter
from .websocket_adapter import WebSocketAdapter
from .conditional_adapter import ConditionalAdapter

# Adaptery specyficzne dla drukarek
from .zpl_adapter import ZplAdapter
from .escpos_adapter import EscPosAdapter
from .pcl_adapter import PclAdapter
from .epcos_adapter import EpcosAdapter

# Tworzenie instancji adapterów
bash = BashAdapter('bash')
http_client = HttpClientAdapter('http_client')
http_server = HttpServerAdapter('http_server')
file_adapter = FileAdapter('file')
python = PythonAdapter('python')
database = DatabaseAdapter('database')
ml = MLAdapter('ml')
message_queue = MessageQueueAdapter('message_queue')
websocket = WebSocketAdapter('websocket')
conditional = ConditionalAdapter('conditional')

# Adaptery drukarek
zpl = ZplAdapter('zpl')
escpos = EscPosAdapter('escpos')
pcl = PclAdapter('pcl')
epcos = EpcosAdapter('epcos')

# Dodaj do sekcji tworzenia instancji adapterów
opencv = OpenCVAdapter('opencv')
rtsp = RtspAdapter('rtsp')
tts = TTSAdapter('tts')
stt = STTAdapter('stt')
rpi_audio = RpiAudioAdapter('rpi_audio')



# Słownik wszystkich adapterów
ADAPTERS = {
    'bash': bash,
    'http_client': http_client,
    'http_server': http_server,
    'file': file_adapter,
    'python': python,
    'database': database,
    'ml': ml,
    'message_queue': message_queue,
    'websocket': websocket,
    'conditional': conditional,
    'zpl': zpl,
    'escpos': escpos,
    'pcl': pcl,
    'epcos': epcos,
    'opencv': opencv,
    'rtsp': rtsp,
    'tts': tts,
    'stt': stt,
    'rpi_audio': rpi_audio
}


# Funkcja pomocnicza do rejestracji nowego adaptera
def register_adapter(adapter_id, adapter_instance):
    """Rejestruje nowy adapter w systemie."""
    if not isinstance(adapter_instance, BaseAdapter):
        raise TypeError("Adapter must be an instance of BaseAdapter")

    ADAPTERS[adapter_id] = adapter_instance
    return adapter_instance