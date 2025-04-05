# Adapter dla systemów kolejkowych
"""
message_queue_adapter.py
"""

# message_queue_adapter.py
from adapters_extended import ChainableAdapter
import json
import time


class MessageQueueAdapter(ChainableAdapter):
    """Adapter dla systemów kolejkowych (Redis, RabbitMQ, Kafka)."""

    def _execute_self(self, input_data=None):
        queue_type = self._params.get('type', 'redis')
        operation = self._params.get('operation', 'publish')
        queue = self._params.get('queue', 'default')

        if queue_type == 'redis':
            return self._handle_redis(operation, queue, input_data)
        elif queue_type == 'rabbitmq':
            return self._handle_rabbitmq(operation, queue, input_data)
        elif queue_type == 'kafka':
            return self._handle_kafka(operation, queue, input_data)
        else:
            raise ValueError(f"Unsupported queue type: {queue_type}")

    def _handle_redis(self, operation, queue, input_data):
        try:
            import redis
        except ImportError:
            raise ImportError("Redis adapter requires 'redis' package. Install with: pip install redis")

        # Konfiguracja połączenia
        host = self._params.get('host', 'localhost')
        port = self._params.get('port', 6379)
        db = self._params.get('db', 0)

        # Utwórz połączenie
        r = redis.Redis(host=host, port=port, db=db)

        if operation == 'publish':
            # Serializuj dane
            if isinstance(input_data, (dict, list)):
                data = json.dumps(input_data)
            else:
                data = str(input_data)

            # Opublikuj wiadomość
            r.rpush(queue, data)

            return {
                'success': True,
                'queue': queue,
                'operation': 'publish',
                'timestamp': time.time()
            }

        elif operation == 'subscribe':
            # Obsługa subskrypcji
            timeout = self._params.get('timeout', 0)

            if timeout > 0:
                # Blokujące pobieranie z timeoutem
                result = r.blpop(queue, timeout=timeout)
                if result:
                    _, data = result
                    # Próba deserializacji JSON
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        return data.decode('utf-8')
                return None
            else:
                # Nieblokujące pobieranie
                data = r.lpop(queue)
                if data:
                    # Próba deserializacji JSON
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        return data.decode('utf-8')
                return None

        else:
            raise ValueError(f"Unsupported Redis operation: {operation}")

    def _handle_rabbitmq(self, operation, queue, input_data):
        try:
            import pika
        except ImportError:
            raise ImportError("RabbitMQ adapter requires 'pika' package. Install with: pip install pika")

        # Konfiguracja połączenia
        host = self._params.get('host', 'localhost')

        # Utwórz połączenie
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()

        # Deklaruj kolejkę
        channel.queue_declare(queue=queue, durable=self._params.get('durable', True))

        if operation == 'publish':
            # Serializuj dane
            if isinstance(input_data, (dict, list)):
                data = json.dumps(input_data)
            else:
                data = str(input_data)

            # Opublikuj wiadomość
            channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=data,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )

            connection.close()

            return {
                'success': True,
                'queue': queue,
                'operation': 'publish',
                'timestamp': time.time()
            }

        elif operation == 'subscribe':
            # Obsługa subskrypcji
            method_frame, header_frame, body = channel.basic_get(queue=queue, auto_ack=True)

            connection.close()

            if method_frame:
                # Próba deserializacji JSON
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    return body.decode('utf-8')

            return None

        else:
            connection.close()
            raise ValueError(f"Unsupported RabbitMQ operation: {operation}")

    def _handle_kafka(self, operation, topic, input_data):
        try:
            from kafka import KafkaProducer, KafkaConsumer
        except ImportError:
            raise ImportError("Kafka adapter requires 'kafka-python' package. Install with: pip install kafka-python")

        # Konfiguracja połączenia
        bootstrap_servers = self._params.get('bootstrap_servers', 'localhost:9092')

        if operation == 'publish':
            # Utwórz producenta
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8') if isinstance(v, (dict, list)) else str(
                    v).encode('utf-8')
            )

            # Wyślij wiadomość
            future = producer.send(topic, input_data)
            producer.flush()
            record_metadata = future.get(timeout=10)

            return {
                'success': True,
                'topic': topic,
                'partition': record_metadata.partition,
                'offset': record_metadata.offset,
                'operation': 'publish',
                'timestamp': time.time()
            }

        elif operation == 'subscribe':
            # Utwórz konsumenta
            group_id = self._params.get('group_id', 'default-group')
            timeout_ms = self._params.get('timeout_ms', 1000)

            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                auto_offset_reset='earliest',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                consumer_timeout_ms=timeout_ms
            )

            # Pobierz wiadomości
            messages = []
            for message in consumer:
                messages.append(message.value)
                if not self._params.get('consume_all', False):
                    break

            consumer.close()

            if not messages:
                return None

            if self._params.get('consume_all', False):
                return messages

            return messages[0] if messages else None

        else:
            raise ValueError(f"Unsupported Kafka operation: {operation}")


# Dodaj adapter do dostępnych adapterów
message_queue = MessageQueueAdapter('message_queue')
ADAPTERS['message_queue'] = message_queue