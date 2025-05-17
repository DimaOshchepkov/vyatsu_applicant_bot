from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from vector_db_service.app.load_collection import load

from vector_db_service.app.api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Это выполняется при старте
    await load()
    yield


app = FastAPI(
    title="Vector Service for Qdrant",
    description="Микросервис для работы с коллекциями Qdrant",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
