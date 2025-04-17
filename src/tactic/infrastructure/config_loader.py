import logging
import os

from dataclasses import dataclass


@dataclass
class BotConfig:
    """Bot config"""

    api_token: str


@dataclass
class BaseDBConfig:
    """Base Database Connection config"""

    db_host: str
    db_name: str
    db_user: str
    db_pass: str

    def get_connection_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}/{self.db_name}"

@dataclass
class QdrantConfig:
    "Qdrant config"
    
    qdrant_host: str
    qdrant_port: str
    qdrant_question_collection: str
    embedded_model: str
    embedded_model_size: int

@dataclass
class DBConfig(BaseDBConfig):
    """Database config"""


@dataclass
class Config:
    """App config"""

    bot: BotConfig
    db: DBConfig
    qdrant: QdrantConfig


@dataclass
class AlembicDB(BaseDBConfig):
    """
    Alembic database config

    need other user for migrations in production.
    """


def load_config() -> Config:
    """Get app config"""

    api_token: str = os.environ["API_TOKEN"]

    db_name: str = os.environ["DB_NAME"]
    db_user: str = os.environ["DB_USER"]
    db_pass: str = os.environ["DB_PASS"]
    db_host: str = os.environ["DB_HOST"]
    
    qdrant_host: str = os.environ["QDRANT_HOST_NAME"]
    qdrant_port: str = os.environ["QDRANT_PORT"]
    qdrant_question_collection: str = os.environ["QDRANT_QUESTION_COLLECTION"]
    embedded_model: str =  os.environ["EMBEDDED_MODEL"]
    embedded_model_size: int = int(os.environ["EMBEDDED_SIZE"])
    return Config(
        bot=BotConfig(api_token=api_token),
        db=DBConfig(
            db_pass=db_pass,
            db_user=db_user,
            db_host=db_host,
            db_name=db_name,
        ),
        qdrant=QdrantConfig(
			qdrant_host=qdrant_host,
			qdrant_port=qdrant_port,
			qdrant_question_collection=qdrant_question_collection,
			embedded_model=embedded_model,
			embedded_model_size=embedded_model_size
		)
    )


def load_alembic_settings() -> AlembicDB:
    """Get alembic settings"""

    db_name: str = os.environ["DB_NAME"]
    db_user: str = os.environ["DB_USER"]
    db_pass: str = os.environ["DB_PASS"]
    db_host: str = os.environ["DB_HOST"]

    logging.info(db_host)

    return AlembicDB(
        db_pass=db_pass,
        db_user=db_user,
        db_host=db_host,
        db_name=db_name,
    )
