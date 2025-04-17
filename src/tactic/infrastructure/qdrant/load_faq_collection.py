import json
import logging
from pathlib import Path
from typing import List

from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

from tactic.infrastructure.config_loader import load_config


# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


# Pydantic-модель для вопросов
class QuestionItem(BaseModel):
    question: str
    path: List[str]
    answer: str


# Класс для эмбеддингов
class SentenceEmbedder:
    def __init__(self, model_name: str):
        logger.info(f"Загрузка модели эмбеддинга: {model_name}")
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str) -> List[float]:
        return self.model.encode([text])[0]


# Загрузка и валидация вопросов из JSON
def load_questions(path: str | Path) -> List[QuestionItem]:
    logger.info(f"Загрузка вопросов из: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    questions = [QuestionItem(**item) for item in raw_data]
    logger.info(f"Загружено {len(questions)} вопросов")
    return questions


# Создание и заполнение коллекции в Qdrant
def recreate_collection_with_data(client: QdrantClient, collection_name: str, vector_size: int,
                                  embedder: SentenceEmbedder, questions: List[QuestionItem]):
    logger.info(f"Проверка существования коллекции '{collection_name}'")
    if collection_name in client.get_collections().collections:
        logger.info(f"Коллекция '{collection_name}' существует. Удаляем...")
        client.delete_collection(collection_name=collection_name)

    logger.info(f"Создание новой коллекции '{collection_name}'")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    logger.info("Генерация эмбеддингов и подготовка данных к загрузке...")
    points = []
    for idx, item in enumerate(questions):
        path_str = " > ".join(item.path)
        combined_text = f"{path_str} — {item.question}"
        vector = embedder.encode(combined_text)

        points.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload=item.model_dump()
            )
        )

    logger.info(f"Загрузка {len(points)} точек в Qdrant...")
    client.upsert(collection_name=collection_name, points=points)
    logger.info("Коллекция успешно создана и заполнена.")


# Точка входа
def main():
    config = load_config().qdrant

    questions_data = load_questions("faq_with_path.json")
    embedder = SentenceEmbedder(model_name=config.embedded_model)

    client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port)

    recreate_collection_with_data(
        client=client,
        collection_name=config.qdrant_question_collection,
        vector_size=config.embedded_model_size,
        embedder=embedder,
        questions=questions_data
    )


if __name__ == "__main__":
    main()
