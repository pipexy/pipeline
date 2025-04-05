#!/usr/bin/env python3
# examples/message_queue_adapter_example.py

from adapters.message_queue_adapter import MessageQueueAdapter
import time


# Example 1: Basic publish and consume
def basic_pubsub_example():
    print("\n--- Message Queue Adapter Example 1: Basic publish and consume ---")

    # Create publisher adapter
    publisher = MessageQueueAdapter({})
    publisher.queue_type("rabbitmq")
    publisher.host("localhost")
    publisher.queue_name("test_queue")

    # Create consumer adapter
    consumer = MessageQueueAdapter({})
    consumer.queue_type("rabbitmq")
    consumer.host("localhost")
    consumer.queue_name("test_queue")

    # Publish a message
    message = {"type": "notification", "text": "Hello from Message Queue Adapter!"}
    publisher.publish(message)
    print(f"Published message: {message}")

    # Consume the message
    def message_handler(msg):
        print(f"Received message: {msg}")
        return True  # Acknowledge the message

    consumer.callback(message_handler)
    print("Starting consumer (will consume for 5 seconds)...")

    # Start consuming in a non-blocking way
    consumer.consume(block=False)

    # Let it run for a bit
    time.sleep(5)

    # Stop consuming
    consumer.stop()
    print("Consumer stopped")


# Example 2: Publish-subscribe pattern with topics
def pubsub_topics_example():
    print("\n--- Message Queue Adapter Example 2: Publish-subscribe with topics ---")

    # Create publisher adapter
    publisher = MessageQueueAdapter({})
    publisher.queue_type("rabbitmq")
    publisher.host("localhost")
    publisher.exchange("news_events")
    publisher.exchange_type("topic")

    # Create consumers for different topics
    sports_consumer = MessageQueueAdapter({})
    sports_consumer.queue_type("rabbitmq")
    sports_consumer.host("localhost")
    sports_consumer.exchange("news_events")
    sports_consumer.exchange_type("topic")
    sports_consumer.routing_key("news.sports.*")

    tech_consumer = MessageQueueAdapter({})
    tech_consumer.queue_type("rabbitmq")
    tech_consumer.host("localhost")
    tech_consumer.exchange("news_events")
    tech_consumer.exchange_type("topic")
    tech_consumer.routing_key("news.tech.*")

    # Publish messages to different topics
    publisher.routing_key("news.sports.football")
    publisher.publish({"title": "Football Match Results", "content": "Team A won 2-1"})

    publisher.routing_key("news.tech.ai")
    publisher.publish({"title": "AI Breakthrough", "content": "New model achieves SOTA results"})

    # Set up handlers for consumers
    def sports_handler(msg):
        print(f"Sports consumer received: {msg}")
        return True

    def tech_handler(msg):
        print(f"Tech consumer received: {msg}")
        return True

    sports_consumer.callback(sports_handler)
    tech_consumer.callback(tech_handler)

    # Start consumers in non-blocking way
    print("Starting topic consumers (will run for 5 seconds)...")
    sports_consumer.consume(block=False)
    tech_consumer.consume(block=False)

    # Let them run for a bit
    time.sleep(5)

    # Stop consumers
    sports_consumer.stop()
    tech_consumer.stop()
    print("Consumers stopped")


# Example 3: Request-reply pattern
def request_reply_example():
    print("\n--- Message Queue Adapter Example 3: Request-reply pattern ---")

    # Create request sender
    requester = MessageQueueAdapter({})
    requester.queue_type("rabbitmq")
    requester.host("localhost")
    requester.queue_name("rpc_queue")

    # Create reply handler
    replier = MessageQueueAdapter({})
    replier.queue_type("rabbitmq")
    replier.host("localhost")
    replier.queue_name("rpc_queue")

    # Define reply handler function
    def calculate_handler(request):
        print(f"Received calculation request: {request}")
        try:
            x = request.get("x", 0)
            y = request.get("y", 0)
            operation = request.get("operation", "add")

            result = None
            if operation == "add":
                result = x + y
            elif operation == "subtract":
                result = x - y
            elif operation == "multiply":
                result = x * y
            elif operation == "divide":
                result = x / y if y != 0 else "Error: Division by zero"

            return {"result": result, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "error"}

    # Set up reply handler
    replier.callback(calculate_handler)

    # Start replier in a separate thread
    print("Starting RPC handler...")
    replier.consume(block=False)

    # Give the replier time to set up
    time.sleep(1)

    # Send RPC requests
    print("Sending RPC requests...")
    add_request = {"x": 5, "y": 3, "operation": "add"}
    add_result = requester.rpc_call(add_request)
    print(f"5 + 3 = {add_result}")

    mult_request = {"x": 4, "y": 7, "operation": "multiply"}
    mult_result = requester.rpc_call(mult_request)
    print(f"4 * 7 = {mult_result}")

    # Stop the replier
    replier.stop()
    print("RPC handler stopped")


if __name__ == "__main__":
    print("Running MessageQueueAdapter examples:")
    basic_pubsub_example()
    pubsub_topics_example()
    request_reply_example()