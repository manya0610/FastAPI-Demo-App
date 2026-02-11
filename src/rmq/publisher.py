import json
import aio_pika
from typing import Any
from fastapi import Request

class RabbitMQPublisher:
    def __init__(self, connection_url: str, queue_name: str):
        self.connection_url = connection_url
        self.queue_name = queue_name
        self.connection = None
        self.channel = None

    async def connect(self):
        """Initializes the connection and channel."""
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(self.connection_url)
            self.channel = await self.connection.channel()
            # Ensure the queue exists before publishing
            await self.channel.declare_queue(self.queue_name, durable=True)

    async def publish(self, message: dict[str, Any]):
        """Publishes a JSON message to the queue."""
        if not self.channel:
            await self.connect()

        body = json.dumps(message).encode()
        
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=self.queue_name,
        )

    async def close(self):
        if self.connection:
            await self.connection.close()