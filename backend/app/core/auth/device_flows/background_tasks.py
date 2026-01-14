import asyncio
from datetime import datetime, timedelta

import pytz
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.auth.device_flows.model import DeviceFlow as DeviceFlowModel
from app.core.logging import logger
from app.database.database import SessionLocal
from app.settings import settings

CHECK_INTERVAL_SECONDS = 3600  # run every hour (60 * 60)


async def cleanup_device_flow_table_task() -> None:
    """
    Periodically clean up stale device flow records.
    Runs every hour to prevent table growth.
    """
    while True:
        with SessionLocal() as db:
            cleanup_device_flow_table(db)

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


def cleanup_device_flow_table(db: Session):
    try:
        logger.info("Cleaning stale device flow entries")
        now = datetime.now(tz=pytz.utc).replace(tzinfo=None)
        cutoff = now - timedelta(minutes=settings.DEVICE_CODE_FLOW_EXPIRY_MINUTES)
        stmt = delete(DeviceFlowModel).where(DeviceFlowModel.max_expiry <= cutoff)
        res = db.execute(stmt)
        db.commit()
        if res.rowcount:
            logger.info(f"Cleaned {res.rowcount} expired device flow entries")
    except Exception as e:
        logger.warning(f"Cleanup device flow entries failed: {e}")
