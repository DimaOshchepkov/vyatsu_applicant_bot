from fastapi import FastAPI
from app.api import router
from app.load_collection import load

load()

app = FastAPI(
    title="Vector Service for Qdrant",
    description="Микросервис для работы с коллекциями Qdrant",
    version="0.1.0"
)

app.include_router(router)
