from fastapi import FastAPI

from contextlib import asynccontextmanager

from src.rmq import rmq_publisher
from src.app.routers.user_router import user_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to RMQ
    await rmq_publisher.connect()
    yield
    # Shutdown: Close RMQ
    await rmq_publisher.close()


app = FastAPI(lifespan=lifespan)



app.include_router(user_router)


