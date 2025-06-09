from tactic.infrastructure.telegram.rate_limited_bot import RateLimitedBot


async def send_delayed_message(ctx, chat_id: int, text: str) -> None:

    bot: RateLimitedBot = ctx["bot"]
    await bot.send_message(chat_id, text)
