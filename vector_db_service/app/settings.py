from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QdrantSettings(BaseSettings):
    qdrant_host_name: str = Field(default="qdrant")
    qdrant_port: int =  Field(default=6333)
    qdrant_question_collection: str = Field(default="vyatsu_faq")
    embedded_size: int = Field(default=312)
    embedded_model: str =  Field(default="cointegrated/rubert-tiny2")
    hub_embedded_model: str =  Field(default="./cointegrated_rubert-tiny2")

    model_config = SettingsConfigDict(
        env_file=".env.vector_db",
        extra="ignore"  
    )

qdrant_settings = QdrantSettings()
