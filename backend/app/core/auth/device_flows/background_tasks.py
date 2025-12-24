import asyncio
from datetime import datetime, timedelta

from sqlalchemy import delete

from app.core.auth.device_flows.model import DeviceFlow as DeviceFlowModel
from app.core.logging import logger
from app.database.database import SessionLocal
from app.settings import settings

CHECK_INTERVAL_SECONDS = 3600  # run every hour (60 * 60)


async def cleanup_device_flows() -> None:
    """
    Periodically clean up stale device flow records.
    Runs every hour to prevent table growth.
    """
    while True:
        try:
            with SessionLocal() as db:
                now = datetime.utcnow()
                cutoff = now - timedelta(
                    minutes=settings.DEVICE_FLOW_CLEANUP_BUFFER_MINUTES
                )
                stmt = delete(DeviceFlowModel).where(
                    DeviceFlowModel.max_expiry <= cutoff
                )
                res = db.execute(stmt)
                db.commit()
                if res.rowcount:
                    logger.info(
                        f"Cleaned {res.rowcount} stale device flow records"
                    )
        except Exception as e:
            # don't crash the loop if something fails
            logger.warning(f"[DeviceFlow] Cleanup task failed: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)