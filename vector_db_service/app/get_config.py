from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    qdrant_host_name: str = "qdrant"
    qdrant_port: int = 6333
    collection_name: str = "faq_collection"
    embedded_size: int = 312
    embedded_model: str = "cointegrated/rubert-tiny2"

    class Config:
        env_file = ".env"

settings = Settings()
