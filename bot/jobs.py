import logging
from datetime import datetime, timezone
from typing import Iterable
from telegram.ext import ContextTypes
from sqlalchemy import select, and_
from db.models import SessionLocal, Subscription, User
from bot.marzban_api import delete_user

logger = logging.getLogger(__name__)


async def cleanup_expired(context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(timezone.utc)
    async with SessionLocal() as session:
        # Find active subscriptions that are past end_at
        result = await session.execute(
            select(Subscription, User)
            .join(User, User.id == Subscription.user_id)
            .where(
                and_(
                    Subscription.status == "active",
                    Subscription.end_at < now,
                )
            )
            .limit(100)
        )
        rows: Iterable[tuple[Subscription, User]] = result.all()
        if not rows:
            logger.debug("No expired subscriptions found")
            return

        for sub, user in rows:
            # Try to delete user in Marzban
            try:
                logger.info(f"Deleting Marzban user {user.marzban_username} due to expired subscription")
                await delete_user(user.marzban_username)
            except Exception:
                logger.exception("Error deleting Marzban user during cleanup")
            # Mark subscription as expired
            sub.status = "expired"

        await session.commit()
        logger.info(f"Expired subscriptions cleaned: {len(rows)}")


