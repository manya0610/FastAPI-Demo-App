from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.routers.auth_router import auth_router
from src.app.routers.user_router import user_router
from src.redis_client import RedisClient
from src.rmq import rmq_publisher


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup: Connect to RMQ
    await rmq_publisher.connect()
    await RedisClient().connect()
    yield
    # Shutdown: Close RMQ
    await rmq_publisher.close()
    await RedisClient().close()


app = FastAPI(lifespan=lifespan)


app.include_router(user_router)
app.include_router(auth_router)
