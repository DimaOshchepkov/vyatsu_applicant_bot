import logging
from typing import List, Union

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from vector_db_service.app.settings import qdrant_settings


# Класс для эмбеддингов
class SentenceEmbedder:
    def __init__(self, model: SentenceTransformer):
        self.model = model

    def encode(self, text: str) -> List[float]:
        return self.model.encode([text])[0]

    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        num_workers: int = 1,
        normalize: bool = True,
        show_progress_bar: bool = False,
    ) -> List[List[float]]:
        """
        Векторизация списка предложений батчами.

        :return: Список векторов (каждый вектор — это список float)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            num_workers=num_workers,
            normalize_embeddings=normalize,
            convert_to_tensor=False,
            show_progress_bar=show_progress_bar,
        )

        if isinstance(embeddings, np.ndarray):
            return embeddings.tolist()
        else:
            raise TypeError(f"Unexpected embeddings type: {type(embeddings)}")


# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)
try:
    logger.info(f"Загрузка эмбеддинг-модели из {qdrant_settings.hub_embedded_model}...")
    sentence_model = SentenceTransformer(qdrant_settings.hub_embedded_model)
    logger.info("Эмбедед модель загружена")
except Exception as e:
    logger.error(f"Не удалось загрузить из {qdrant_settings.hub_embedded_model}")
    logger.error(e)
    raise e


embedder = SentenceEmbedder(sentence_model)
