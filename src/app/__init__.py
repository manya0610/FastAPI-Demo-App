from fastapi import FastAPI

from src.app.routers.user_router import user_router

app = FastAPI()

app.include_router(user_router)
