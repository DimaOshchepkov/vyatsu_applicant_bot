# embedding_model.py
import logging
from pathlib import Path
from typing import List

from sentence_transformers import SentenceTransformer

from app.settings import qdrant_settings


# Класс для эмбеддингов
class SentenceEmbedder:
    def __init__(self, model: SentenceTransformer):
        self.model = model

    def encode(self, text: str) -> List[float]:
        return self.model.encode([text])[0]


# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)
try:
    logger.info(f"Загрузка эмбеддинг-модели из {qdrant_settings.hub_embedded_model}...")
    model_path = Path(qdrant_settings.hub_embedded_model)
    if model_path.exists():
        sentence_model = SentenceTransformer(qdrant_settings.hub_embedded_model)
    else:
        logger.info(
            f"Не удалось загрузить {qdrant_settings.hub_embedded_model}. Загрузка из {qdrant_settings.embedded_model}"
        )
        sentence_model = SentenceTransformer(qdrant_settings.embedded_model)

    logger.info("Эмбедед модель загружена")
except Exception as e:
    logger.info(
        f"Не удалось загрузить из {model_path} и из {qdrant_settings.hub_embedded_model}"
    )
