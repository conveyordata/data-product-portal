import asyncio

from app.core.auth.device_flows.service import DeviceFlowService
from app. core.logging import logger
from app.database.database import SessionLocal

CHECK_INTERVAL_SECONDS = 3600  # run every hour (60 * 60)


async def cleanup_device_flows() -> None:
    """
    Periodically clean up stale device flow records.
    Runs every hour to prevent table growth.
    """
    service = DeviceFlowService()
    
    while True:
        try:
            with SessionLocal() as db:
                service.clean_device_flows(db)
        except Exception as e:
            # don't crash the loop if something fails
            logger.warning(f"[DeviceFlow] Cleanup task failed: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)