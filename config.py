import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MARZBAN_API_URL = os.getenv("MARZBAN_API_URL", "")
MARZBAN_API_KEY = os.getenv("MARZBAN_API_KEY", "")
MARZBAN_USERNAME = os.getenv("MARZBAN_USERNAME", "")
MARZBAN_PASSWORD = os.getenv("MARZBAN_PASSWORD", "")
POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql+asyncpg://vpn_user:vpn_pass@db:5432/vpn_db")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
