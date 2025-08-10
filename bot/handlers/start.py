from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from db.models import SessionLocal, User

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    username = update.effective_user.username

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == tg_id)
        )
        user = result.scalars().first()
        if user is None:
            marzban_username = username or f"tg_{tg_id}"
            user = User(
                telegram_id=tg_id,
                username=username,
                marzban_username=marzban_username,
            )
            session.add(user)
            await session.commit()

    await update.message.reply_text(
        "Привет! Добро пожаловать в VPN-бот. Команды:\n" \
        "- /profile — профиль и подписка\n" \
        "- /trial — получить тестовый доступ"
    )
