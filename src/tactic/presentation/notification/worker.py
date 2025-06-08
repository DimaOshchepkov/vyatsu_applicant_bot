from arq.connections import RedisSettings

from tactic.presentation.notification.send_delayed_message import send_delayed_message
from tactic.settings import redis_settings


class WorkerSettings:
    functions = [send_delayed_message]
    redis_settings = RedisSettings(
        host=redis_settings.redis_host, port=redis_settings.redis_port
    )
