import asyncio
import json
import logging
from contextlib import asynccontextmanager

from aio_pika import IncomingMessage, connect
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.database import get_db
from src.schemas.user_schema import UserCreate
from src.services.user_service import UserService

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection string (Use your actual DB URL)
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def process_message(message: IncomingMessage):
    # Using .process() automatically ACKs the message if no error occurs.
    async with message.process():
        logger.info(" [x] Received message:")

        # 1. Create a fresh session for this specific message
        async_get_db = asynccontextmanager(get_db)
        async with async_get_db() as session:
            try:
                service = UserService(session)

                # Assume the message body is a username for this example
                data_dict = json.loads(message.body.decode())
                user_data = UserCreate(**data_dict)

                # 2. Use your existing Service Layer logic
                await service.register_user(user_data)

                logger.info(" [v] Successfully registered user %s", data_dict)
            except Exception:
                logger.exception(" [!] Failed to process user")
                # Re-raise to trigger NACK if you want RabbitMQ to retry
                raise


async def main():
    # 1. Connect to RabbitMQ
    connection = await connect("amqp://guest:guest@localhost/")

    async with connection:
        # 2. Open a channel
        channel = await connection.channel()

        # 3. Set QoS (Quality of Service)
        # This limits how many messages the worker grabs at once
        await channel.set_qos(prefetch_count=10)

        # 4. Declare the queue
        queue = await channel.declare_queue("user_registration_queue", durable=True)

        logger.info(" [*] Waiting for messages. To exit press CTRL+C")

        # 5. Start consuming
        await queue.consume(process_message)

        # Keep the worker running forever
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped.")
