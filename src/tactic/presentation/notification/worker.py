from arq.connections import RedisSettings
from redis.asyncio import Redis

from tactic.infrastructure.config_loader import load_config
from tactic.infrastructure.telegram.rate_limited_bot import RateLimitedBot, RedisLimiterBackend
from tactic.presentation.notification.send_delayed_message import send_delayed_message
from tactic.settings import redis_settings



async def startup(ctx):
    config = load_config()

    token = config.bot.api_token
    backend = RedisLimiterBackend(
        redis=Redis(
            host=redis_settings.redis_host,
            port=redis_settings.redis_port,
        )
    )

    bot = RateLimitedBot(token=token, limiter_backend=backend)
    ctx["bot"] = bot

async def shutdown(ctx):
    await ctx["bot"].session.close()
    
class WorkerSettings:
    functions = [send_delayed_message]
    on_startup = startup
    on_shutdown = shutdown
    keep_result=0
    allow_abort_jobs=True
    redis_settings = RedisSettings(
        host=redis_settings.redis_host, port=redis_settings.redis_port
    )

