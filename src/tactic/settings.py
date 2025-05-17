from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExamServiceSettings(BaseSettings):
    exam_json_path: Path = Path("")
    threshold: int = 70

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


exam_service_settings = ExamServiceSettings()


class VectorDbServiceSettings(BaseSettings):

    vector_db_service_container_name: str = Field(default="vector_db_service")

    vector_db_service_port: int = Field(default=8000)

    model_config = SettingsConfigDict(env_file=".env.vector_db", extra="ignore")

    def get_connection_string(self) -> str:
        return f"http://{self.vector_db_service_container_name}:{self.vector_db_service_port}"


vector_db_service_settings = VectorDbServiceSettings()
