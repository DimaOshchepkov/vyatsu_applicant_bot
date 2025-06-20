import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

env = os.getenv("APP_ENV", "development")

if env != "docker":
    load_dotenv(".env.test", override=True)
    if Path(".env.test.local").exists():
        load_dotenv(".env.test.local", override=True)

class TestDBSettings(BaseSettings):
    db_host: str = Field(default="", description="Database host")
    db_port: int = Field(default=-1, description="Database port")
    db_name: str = Field(default="", description="Database name")
    db_user: str = Field(default="", description="Database user")
    db_pass: str = Field(default="", description="Database password")

    model_config = SettingsConfigDict(
        env_file=".env.test",
        extra="ignore"  
    )

    def get_connection_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        
settings = TestDBSettings()


class TestRedisSettings(BaseSettings):
    redis_host: str = Field(default="")
    redis_port: int = Field(default=-1)

    model_config = SettingsConfigDict(env_file=".env.test", extra="ignore")

    def get_connection_string(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    def get_async_connection_string(self) -> str:
        return f"async+redis://{self.redis_host}:{self.redis_port}"


test_redis_settings = TestRedisSettings()