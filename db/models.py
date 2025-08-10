import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone

from config import DATABASE_URL, LOG_LEVEL

logger = logging.getLogger(__name__)
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.DEBUG))

Base = declarative_base()
logger.debug(f"Creating DB engine for {DATABASE_URL}")
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    marzban_username = Column(String, unique=True)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    is_trial = Column(Boolean, default=False, nullable=False)
    status = Column(String, default="active", nullable=False)  # active | expired | canceled
    start_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    end_at = Column(DateTime(timezone=True), nullable=False)
