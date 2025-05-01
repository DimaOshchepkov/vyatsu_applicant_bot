from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    exam_json_path: Path = Path('')
    threshold: int = 70


    class Config:
        env_file = ".env"  # откуда брать переменные окружения
        env_file_encoding = "utf-8"

# Создаём синглтон
settings = Settings()