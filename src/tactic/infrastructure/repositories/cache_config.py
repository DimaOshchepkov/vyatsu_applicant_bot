import hashlib
import inspect
import json

from aiocache import caches

from tactic.settings import redis_settings


def setup_cache():
    caches.set_config(
        {
            "default": {
                "cache": "aiocache.RedisCache",
                "endpoint": redis_settings.redis_host,
                "port": redis_settings.redis_port,
                "password": None,
                "timeout": 1,
                "namespace": "main",
                "serializer": {"class": "aiocache.serializers.PickleSerializer"},
                "plugins": [
                    {"class": "aiocache.plugins.HitMissRatioPlugin"},
                    {"class": "aiocache.plugins.TimingPlugin"},
                ],
            }
        }
    )


def classaware_key_builder(fn, *args, **kwargs) -> str:
    # Имя класса, если есть
    class_name = (
        args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else ""
    )

    # Получаем сигнатуру и связываем переданные аргументы
    sig = inspect.signature(fn)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()

    # Преобразуем в сериализуемый словарь
    key_data = {k: bound.arguments[k] for k in bound.arguments}

    # Хешируем аргументы, чтобы избежать слишком длинных ключей
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()

    return f"{class_name}:{fn.__name__}:{key_hash}"
