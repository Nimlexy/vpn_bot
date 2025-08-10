import asyncio
import logging
from db.models import Base, engine

logger = logging.getLogger(__name__)


async def init_db() -> None:
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema is up to date.")


if __name__ == "__main__":
    asyncio.run(init_db())
