import logging
import aiohttp
from typing import Optional
from config import (
    MARZBAN_API_URL,
    MARZBAN_API_KEY,
    MARZBAN_USERNAME,
    MARZBAN_PASSWORD,
)


logger = logging.getLogger(__name__)
_cached_token: Optional[str] = None


def _auth_headers():
    global _cached_token
    token = MARZBAN_API_KEY or _cached_token
    return {"Authorization": f"Bearer {token}"} if token else {}


async def _login_if_needed(session: aiohttp.ClientSession) -> bool:
    global _cached_token
    if MARZBAN_API_KEY:
        return True
    if not (MARZBAN_USERNAME and MARZBAN_PASSWORD):
        return False

    url = f"{MARZBAN_API_URL.rstrip('/')}/api/admin/token"
    try:
        logger.debug("Logging in to Marzban to obtain token...")
        async with session.post(url, json={"username": MARZBAN_USERNAME, "password": MARZBAN_PASSWORD}, timeout=15) as resp:
            if resp.status == 200:
                data = await resp.json()
                _cached_token = data.get("access_token") or data.get("token")
                logger.info("Obtained Marzban token via admin credentials")
                return _cached_token is not None
            logger.error(f"Login failed with status {resp.status}")
            return False
    except aiohttp.ClientError:
        logger.exception("Failed to login to Marzban")
        return False


async def get_user_info(marzban_username: str):
    if not MARZBAN_API_URL:
        return None

    url = f"{MARZBAN_API_URL.rstrip('/')}/api/user/{marzban_username}"
    async with aiohttp.ClientSession() as session:
        try:
            # ensure we have a token
            if not MARZBAN_API_KEY and not _cached_token:
                await _login_if_needed(session)

            async with session.get(url, headers=_auth_headers(), timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.debug(f"Fetched Marzban user info for {marzban_username}")
                    return data
                if resp.status == 401 and (MARZBAN_USERNAME and MARZBAN_PASSWORD):
                    # try re-login once
                    if await _login_if_needed(session):
                        async with session.get(url, headers=_auth_headers(), timeout=15) as retry_resp:
                            if retry_resp.status == 200:
                                data = await retry_resp.json()
                                logger.debug(f"Fetched Marzban user info after re-login for {marzban_username}")
                                return data
                return None
        except aiohttp.ClientError:
            logger.exception("Error fetching Marzban user info")
            return None


async def create_user(m_username: str, data_limit: Optional[int] | None = None, expire_at: Optional[int] | None = None) -> bool:
    if not MARZBAN_API_URL:
        return False
    url = f"{MARZBAN_API_URL.rstrip('/')}/api/user"
    payload = {"username": m_username}
    if data_limit is not None:
        payload["data_limit"] = data_limit
    if expire_at is not None:
        payload["expire"] = expire_at
    async with aiohttp.ClientSession() as session:
        try:
            if not MARZBAN_API_KEY and not _cached_token:
                await _login_if_needed(session)
            async with session.post(url, headers=_auth_headers(), json=payload, timeout=15) as resp:
                ok = resp.status in (200, 201)
                if ok:
                    logger.info(f"Created Marzban user {m_username}")
                else:
                    logger.error(f"Failed to create Marzban user {m_username}, status {resp.status}")
                return ok
        except aiohttp.ClientError:
            logger.exception("Error creating Marzban user")
            return False


async def delete_user(m_username: str) -> bool:
    if not MARZBAN_API_URL:
        return False
    url = f"{MARZBAN_API_URL.rstrip('/')}/api/user/{m_username}"
    async with aiohttp.ClientSession() as session:
        try:
            if not MARZBAN_API_KEY and not _cached_token:
                await _login_if_needed(session)
            async with session.delete(url, headers=_auth_headers(), timeout=15) as resp:
                ok = resp.status in (200, 204)
                if ok:
                    logger.info(f"Deleted Marzban user {m_username}")
                else:
                    logger.error(f"Failed to delete Marzban user {m_username}, status {resp.status}")
                return ok
        except aiohttp.ClientError:
            logger.exception("Error deleting Marzban user")
            return False
