from aiogram import Bot


async def send_delayed_message(ctx, chat_id: int, text: str) -> None:

    bot: Bot = ctx["bot"]
    await bot.send_message(chat_id, text)
