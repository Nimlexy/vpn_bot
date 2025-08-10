import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from bot.handlers.start import start
from bot.handlers.profile import profile
from bot.handlers.trial import trial
from init_db import init_db


def main() -> None:
    # Ensure an event loop exists (Python 3.11)
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    async def _post_init(app):
        await init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(_post_init).concurrent_updates(False).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("trial", trial))

    app.run_polling()


if __name__ == "__main__":
    main()
