import json
import logging
import os
from pathlib import Path
from typing import List

from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.embedding_model import SentenceEmbedder, sentence_model
from app.settings import qdrant_settings

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


# Загрузка и валидация вопросов из JSON
def load_questions(path: str | Path) -> List[QuestionItem]:
    logger.info(f"Загрузка вопросов из: {path}")
    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    questions = [QuestionItem(**item) for item in raw_data]
    logger.info(f"Загружено {len(questions)} вопросов")
    return questions


# Создание и заполнение коллекции в Qdrant
def recreate_collection_with_data(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
    embedder: SentenceEmbedder,
    questions: List[QuestionItem],
):
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]
    if collection_name in collection_names:
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

        points.append(PointStruct(id=idx, vector=vector, payload=item.model_dump()))

    logger.info(f"Загрузка {len(points)} точек в Qdrant...")
    client.upsert(collection_name=collection_name, points=points)
    logger.info("Коллекция успешно создана и заполнена.")


# Точка входа
def load():

    base_dir = os.path.dirname(__file__)
    full_path = os.path.join(base_dir, "faq_with_path.json")
    questions_data = load_questions(full_path)

    client = QdrantClient(
        host=qdrant_settings.qdrant_host_name, port=qdrant_settings.qdrant_port
    )

    recreate_collection_with_data(
        client=client,
        collection_name=qdrant_settings.qdrant_question_collection,
        vector_size=qdrant_settings.embedded_size,
        embedder=sentence_model,
        questions=questions_data,
    )
