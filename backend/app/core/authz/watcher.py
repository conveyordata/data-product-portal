import asyncio
import contextlib
from typing import Callable

import asyncpg
from sqlalchemy import text

from app.core.logging import logger
from app.database.database import engine, get_url

CHANNEL = "casbin_policy_update"


def notify_policy_update() -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text(f"NOTIFY {CHANNEL}"))
            conn.commit()
        logger.debug("[authz] Sent casbin NOTIFY")
    except Exception as exc:
        logger.warning("[authz] Failed to send casbin NOTIFY: %s", exc)


async def listen_for_policy_changes(on_change: Callable[[], None]) -> None:
    loop = asyncio.get_running_loop()

    while True:
        conn = None
        try:
            conn = await asyncpg.connect(get_url())

            async def _cb(conn, pid, channel, payload):  # noqa: ARG001
                logger.debug("[authz] Received policy update notification, reloading")
                try:
                    await loop.run_in_executor(None, on_change)
                except Exception as exc:
                    logger.warning("[authz] reload_policy failed: %s", exc)

            await conn.add_listener(CHANNEL, _cb)
            logger.info("[authz] Watcher listening on channel '%s'", CHANNEL)
            await asyncio.Future()
        except asyncio.CancelledError:
            if conn:
                await conn.close()
            raise
        except Exception as exc:
            if conn:
                with contextlib.suppress(Exception):
                    await conn.close()
            logger.warning(
                "[authz] Casbin watcher disconnected (%s), retrying in 5 s", exc
            )
            await asyncio.sleep(5)
