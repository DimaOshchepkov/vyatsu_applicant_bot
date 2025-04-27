# embedding_model.py
from sentence_transformers import SentenceTransformer
from typing import List
import logging
from .get_config import settings
from pathlib import Path

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
logger.info(f"Загрузка эмбеддинг-модели {settings.embedded_model}...")
model_path = Path(settings.embedded_model)
sentence_model = SentenceTransformer(settings.embedded_model if model_path.exists() else settings.hub_embedded_model)
logger.info("Эмбедед модель загружена")