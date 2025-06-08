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


class DBSettings(BaseSettings):
    db_host: str = Field(default="", description="Database host")
    db_port: int = Field(default=-1, description="Database port")
    db_name: str = Field(default="", description="Database name")
    db_user: str = Field(default="", description="Database user")
    db_pass: str = Field(default="", description="Database password")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def get_connection_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


db_settings = DBSettings()


class RedisSettings(BaseSettings):
    redis_host: str = Field(default='bot_redis')
    redis_port: int = Field(default=6379)
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def get_connection_string(self) -> str:
        return f'redis://{self.redis_host}:{self.redis_port}'
    
    def get_async_connection_string(self) -> str:
        return f'async+redis://{self.redis_host}:{self.redis_port}'
    
redis_settings = RedisSettings()
