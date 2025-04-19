# embedding_model.py
from sentence_transformers import SentenceTransformer
from typing import List
import logging
from app.get_config import settings

# Класс для эмбеддингов
class SentenceEmbedder:
    def __init__(self, model: SentenceTransformer):
        self.model = model

    def encode(self, text: str) -> List[float]:
        return self.model.encode([text])[0]

logger = logging.getLogger(__name__)
logger.info("Загрузка эмбеддинг-модели...")
sentence_model = SentenceTransformer(settings.collection_name)
logger.info("Эмбедед модель загружена")