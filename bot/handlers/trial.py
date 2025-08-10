from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from db.models import SessionLocal, User, Subscription
from bot.marzban_api import create_user


TRIAL_DAYS = 1
TRIAL_LIMIT_MB = 500  # 500 MB


async def trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id

    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = result.scalars().first()
        if user is None:
            await update.message.reply_text("Сначала напиши /start")
            return

        # already has active subscription
        sub_q = await session.execute(
            select(Subscription).where(Subscription.user_id == user.id, Subscription.status == "active")
        )
        existing = sub_q.scalars().first()
        if existing is not None:
            await update.message.reply_text("У тебя уже есть активный доступ.")
            return

        end_at = datetime.now(timezone.utc) + timedelta(days=TRIAL_DAYS)
        # Marzban expects expire as unix timestamp (seconds)
        expire_ts = int(end_at.timestamp())
        data_limit_bytes = TRIAL_LIMIT_MB * 1024 * 1024

        ok = await create_user(user.marzban_username, data_limit=data_limit_bytes, expire_at=expire_ts)
        if not ok:
            await update.message.reply_text("Не удалось выдать тестовый доступ. Попробуй позже.")
            return

        sub = Subscription(
            user_id=user.id,
            is_trial=True,
            status="active",
            start_at=datetime.now(timezone.utc),
            end_at=end_at,
        )
        session.add(sub)
        await session.commit()

        await update.message.reply_text(
            f"Выдан тестовый доступ на {TRIAL_DAYS} дн., лимит {TRIAL_LIMIT_MB} MB. Смотри /profile"
        )


