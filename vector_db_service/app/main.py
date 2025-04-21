from fastapi import FastAPI
from .api import router
from .load_collection import load
from contextlib import asynccontextmanager
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Это выполняется при старте
    load()
    yield

app = FastAPI(
    title="Vector Service for Qdrant",
    description="Микросервис для работы с коллекциями Qdrant",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

