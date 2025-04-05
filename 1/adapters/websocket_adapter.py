# Adapter dla WebSocket
"""
websocket_adapter.py
"""

# websocket_adapter.py
from adapters import ChainableAdapter
import json
import threading
import time


class WebSocketAdapter(ChainableAdapter):
    """Adapter do komunikacji przez WebSockety."""

    _connections = {}  # Przechowuje aktywne połączenia

    def _execute_self(self, input_data=None):
        operation = self._params.get('operation', 'connect')

        if operation == 'connect':
            return self._connect()
        elif operation == 'send':
            return self._send(input_data)
        elif operation == 'receive':
            return self._receive()
        elif operation == 'close':
            return self._close()
        elif operation == 'serve':
            return self._serve()
        else:
            raise ValueError(f"Unsupported WebSocket operation: {operation}")

    def _connect(self):
        try:
            import websocket
        except ImportError:
            raise ImportError(
                "WebSocket adapter requires 'websocket-client' package. Install with: pip install websocket-client")

        url = self._params.get('url')
        if not url:
            raise ValueError("WebSocket adapter requires 'url' parameter for connect operation")

        # Generuj ID połączenia
        connection_id = f"ws_{int(time.time())}_{id(self)}"

        # Utwórz połączenie
        ws = websocket.create_connection(url)
        WebSocketAdapter._connections[connection_id] = ws

        return {
            'success': True,
            'connection_id': connection_id,
            'url': url,
            'operation': 'connect',
            'timestamp': time.time()
        }

    def _send(self, input_data):
        connection_id = self._params.get('connection_id')
        if not connection_id or connection_id not in WebSocketAdapter._connections:
            raise ValueError(f"Invalid or missing connection_id. Use 'connect' operation first.")

        ws = WebSocketAdapter._connections[connection_id]

        # Serializuj dane jeśli potrzeba
        if isinstance(input_data, (dict, list)):
            data = json.dumps(input_data)
        else:
            data = str(input_data)

        # Wyślij wiadomość
        ws.send(data)

        return {
            'success': True,
            'connection_id': connection_id,
            'operation': 'send',
            'timestamp': time.time()
        }

    def _receive(self):
        connection_id = self._params.get('connection_id')
        if not connection_id or connection_id not in WebSocketAdapter._connections:
            raise ValueError(f"Invalid or missing connection_id. Use 'connect' operation first.")

        ws = WebSocketAdapter._connections[connection_id]
        timeout = self._params.get('timeout', 0)

        if timeout > 0:
            ws.settimeout(timeout)

        # Odbierz wiadomość
        try:
            data = ws.recv()

            # Próbuj sparsować jako JSON
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        except Exception as e:
            if timeout > 0:
                return None
            raise RuntimeError(f"Error receiving WebSocket message: {e}")

    def _close(self):
        connection_id = self._params.get('connection_id')
        if not connection_id or connection_id not in WebSocketAdapter._connections:
            return {'success': False, 'error': 'Invalid connection ID'}

        ws = WebSocketAdapter._connections[connection_id]
        ws.close()
        del WebSocketAdapter._connections[connection_id]

        return {
            'success': True,
            'connection_id': connection_id,
            'operation': 'close',
            'timestamp': time.time()
        }

    def _serve(self):
        try:
            from simple_websocket_server import WebSocketServer, WebSocket
        except ImportError:
            raise ImportError(
                "WebSocket server requires 'simple-websocket-server' package. Install with: pip install simple-websocket-server")

        port = self._params.get('port', 8765)
        host = self._params.get('host', '0.0.0.0')

        # Handler na wiadomości
        handler_code = self._params.get('handler', '')

        # Tworzymy klasę handlera
        class MessageHandler(WebSocket):
            def handle(self):
                message = self.data

                # Próbuj sparsować jako JSON
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    data = message

                # Wykonaj kod handlera
                if handler_code:
                    global_vars = {
                        'data': data,
                        'socket': self,
                        'response': None
                    }
                    exec(handler_code, global_vars)

                    # Jeśli ustawiono odpowiedź, wyślij ją
                    response = global_vars.get('response')
                    if response:
                        if isinstance(response, (dict, list)):
                            self.send_message(json.dumps(response))
                        else:
                            self.send_message(str(response))

            def connected(self):
                print(f"WebSocket client connected: {self.address}")

            def handle_close(self):
                print(f"WebSocket client disconnected: {self.address}")

        # Uruchom serwer w osobnym wątku
        server = WebSocketServer(host, port, MessageHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        return {
            'success': True,
            'host': host,
            'port': port,
            'server': server,
            'thread': server_thread,
            'operation': 'serve',
            'timestamp': time.time()
        }


# Dodaj adapter do dostępnych adapterów
websocket = WebSocketAdapter('websocket')
ADAPTERS['websocket'] = websocket