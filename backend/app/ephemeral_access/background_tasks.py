import asyncio

from sqlalchemy import func, update

from app.core.logging import logger
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.status import DataProductStatus
from app.database.database import SessionLocal

CLEANUP_INTERVAL_SECONDS = 300  # 5 minutes
STARTUP_DELAY_SECONDS = 60  # avoid blocking event loop during startup


async def cleanup_expired_ephemeral_data_products() -> None:
    await asyncio.sleep(STARTUP_DELAY_SECONDS)
    while True:
        try:
            with SessionLocal() as db:
                result = db.execute(
                    update(DataProductModel)
                    .where(DataProductModel.is_ephemeral == True)  # noqa: E712
                    .where(DataProductModel.expires_at <= func.now())
                    .where(DataProductModel.status != DataProductStatus.ARCHIVED)
                    .values(status=DataProductStatus.ARCHIVED)
                )
                if result.rowcount > 0:
                    db.commit()
                    logger.info(
                        f"[Ephemeral] Archived {result.rowcount} expired ephemeral data product(s)"
                    )

        except Exception as e:
            logger.warning(f"[Ephemeral] Cleanup failed: {e}")

        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
