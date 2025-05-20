from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QdrantSettings(BaseSettings):
    qdrant_host_name: str = Field(default="qdrant")
    qdrant_port: int =  Field(default=6333)
    qdrant_question_collection: str = Field(default="vyatsu_faq")
    qdrant_program_collection: str = Field(default="program_vectors")
    embedded_size: int = Field(default=312)
    embedded_model: str =  Field(default="cointegrated/rubert-tiny2")
    hub_embedded_model: str =  Field(default="./cointegrated_rubert-tiny2")

    model_config = SettingsConfigDict(
        env_file=".env.vector_db",
        extra="ignore"  
    )


qdrant_settings = QdrantSettings()


class DBSettings(BaseSettings):
    db_host: str = Field(default="", description="Database host")
    db_port: int = Field(default=-1, description="Database port")
    db_name: str = Field(default="", description="Database name")
    db_user: str = Field(default="", description="Database user")
    db_pass: str = Field(default="", description="Database password")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  
    )

    def get_connection_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        
        
db_settings = DBSettings()
