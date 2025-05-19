from aiocache import caches
from tactic.settings import redis_settings
from aiocache.serializers import PickleSerializer


def setup_cache():
    caches.set_config({
        'default': {
            'cache': "aiocache.RedisCache",
            'endpoint': redis_settings.redis_host,
            'port': redis_settings.redis_port,
            'password': None,
            'timeout': 1,
            'namespace': "main",
            'serializer': {
                'class': "aiocache.serializers.PickleSerializer"
            },
            'plugins': [
                {'class': "aiocache.plugins.HitMissRatioPlugin"},
                {'class': "aiocache.plugins.TimingPlugin"}
            ]
        }
    })
    
    
def classaware_key_builder(fn, *args, **kwargs) -> str:
    class_name = args[0].__class__.__name__ if args else ""
    return f"{class_name}:{fn.__name__}"