from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

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