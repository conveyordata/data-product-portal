import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.abstract_data_product.model import AbstractDataProduct
from app.core.logging import logger
from app.data_products.status import DataProductStatus
from app.database.database import SessionLocal

CHECK_INTERVAL_SECONDS = 600  # run every 10 minutes
STUCK_THRESHOLD_SECONDS = 3600  # warn after 1 hour in DELETING


async def check_stuck_deletions() -> None:
    while True:
        try:
            with SessionLocal() as db:
                stuck = (
                    db.execute(
                        select(AbstractDataProduct).where(
                            AbstractDataProduct.status == DataProductStatus.DELETING
                        )
                    )
                    .scalars()
                    .all()
                )
                now = datetime.now(tz=timezone.utc)
                for adp in stuck:
                    last_updated = adp.updated_on
                    if last_updated is None:
                        continue
                    # updated_on is stored without timezone; treat as UTC
                    if last_updated.tzinfo is None:
                        last_updated = last_updated.replace(tzinfo=timezone.utc)

                    age_seconds = (now - last_updated).total_seconds()
                    if age_seconds >= STUCK_THRESHOLD_SECONDS:
                        logger.warning(
                            f"[Finalizers] {adp.abstract_data_product_type.value} '{adp.name}' "
                            f"(id={adp.id}) has been stuck in DELETING for "
                            f"{int(age_seconds // 60)} minutes. "
                            f"Remaining finalizers: {adp.finalizers}"
                        )
        except Exception as e:
            logger.warning(f"[Finalizers] Stuck deletion check failed: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
