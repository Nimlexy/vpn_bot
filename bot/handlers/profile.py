import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from db.models import SessionLocal, User, Subscription
from bot.marzban_api import get_user_info

logger = logging.getLogger(__name__)

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id

    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = result.scalars().first()
        if user is None:
            await update.message.reply_text("Ты не зарегистрирован. Напиши /start.")
            return

        marzban_info = await get_user_info(user.marzban_username)
        if not marzban_info:
            logger.info("No Marzban info found for user, likely no active access")
            await update.message.reply_text("В Marzban нет активного доступа. Оформи /trial или оплату.")
            return

        usage = marzban_info.get('used_traffic', 0)
        limit = marzban_info.get('data_limit', None)
        expire = marzban_info.get('expire', None)

        def fmt_bytes(value):
            try:
                mb = float(value) / (1024 * 1024)
                return f"{mb:.2f} MB"
            except Exception:
                return str(value)

        # subscription info
        sub_result = await session.execute(
            select(Subscription).where(Subscription.user_id == user.id, Subscription.status == "active")
        )
        sub = sub_result.scalars().first()

        text_lines = ["👤 *Профиль*", f"Marzban: `{user.marzban_username}`"]
        if expire is not None:
            text_lines.append(f"📅 Истекает: `{expire}`")
        text_lines.append(f"📊 Использовано: `{fmt_bytes(usage)}`")
        if limit is not None:
            text_lines.append(f"🔒 Лимит: `{fmt_bytes(limit)}`")
        if sub is not None:
            text_lines.append(f"📌 Подписка: `{'trial' if sub.is_trial else 'paid'}` до `{sub.end_at}`")

        text = "\n".join(text_lines)

        await update.message.reply_text(text, parse_mode="Markdown")
