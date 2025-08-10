import os
from urllib.parse import urlparse

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MARZBAN_API_URL = os.getenv("MARZBAN_API_URL", "")
MARZBAN_API_KEY = os.getenv("MARZBAN_API_KEY", "")
MARZBAN_USERNAME = os.getenv("MARZBAN_USERNAME", "")
MARZBAN_PASSWORD = os.getenv("MARZBAN_PASSWORD", "")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

# Database selection: prefer explicit Postgres DSN if provided,
# otherwise use SQLite file in DB_PATH (default /app/data/bot.db)
POSTGRES_DSN = os.getenv("POSTGRES_DSN", "")
DB_PATH = os.getenv("DB_PATH", "/app/data")
if POSTGRES_DSN:
    DATABASE_URL = POSTGRES_DSN
else:
    os.makedirs(DB_PATH, exist_ok=True)
    DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(DB_PATH, 'bot.db')}"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
