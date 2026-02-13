from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.routers.user_router import user_router
from src.redis_client import redis_manager
from src.rmq import rmq_publisher


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup: Connect to RMQ
    await redis_manager.connect()
    await rmq_publisher.connect()
    yield
    # Shutdown: Close RMQ
    await redis_manager.close()
    await rmq_publisher.close()


app = FastAPI(lifespan=lifespan)


app.include_router(user_router)
