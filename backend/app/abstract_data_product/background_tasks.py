import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.abstract_data_product.input_ports.model import InputPort
from app.abstract_data_product.model import AbstractDataProduct
from app.authorization.role_assignments.enums import DecisionStatus
from app.core.logging import logger
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.status import AbstractDataProductStatus
from app.database.database import SessionLocal
from app.exceptions import InvalidInputPortState

CHECK_INTERVAL_SECONDS = 600  # run every 10 minutes
STUCK_THRESHOLD_SECONDS = 3600  # warn after 1 hour in DELETING

INPUT_PORT_EXPIRY_CHECK_INTERVAL_SECONDS = 3600  # run every hour


async def check_stuck_deletions() -> None:
    while True:
        try:
            with SessionLocal() as db:
                stuck = (
                    db.execute(
                        select(AbstractDataProduct).where(
                            AbstractDataProduct.status
                            == AbstractDataProductStatus.DELETING
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


async def expire_input_ports() -> None:
    while True:
        try:
            with SessionLocal() as db:
                now = datetime.now(tz=timezone.utc)
                expired_ports = (
                    db.execute(
                        select(InputPort)
                        .where(InputPort.status == DecisionStatus.APPROVED)
                        .where(InputPort.expires_on != None)  # noqa: E711
                        .where(InputPort.expires_on <= now)
                    )
                    .scalars()
                    .unique()
                    .all()
                )
                for input_port in expired_ports:
                    if not input_port.is_renewing:
                        logger.info(
                            f"[InputPort Expiry] Expiring input port {input_port.id} "
                            f"for dataset {input_port.dataset_id} and consuming data product "
                            f"{input_port.consuming_abstract_data_product_id}."
                        )
                        input_port.expired_on = now
                        input_port.status = DecisionStatus.EXPIRED
                    elif (
                        input_port.is_renewing
                        and input_port.dataset.access_type
                        != OutputPortAccessType.UNRESTRICTED
                    ):
                        logger.info(
                            f"[InputPort Expiry] Placing input port {input_port.id} under Pending"
                            f"for dataset {input_port.dataset_id} and consuming data product "
                            f"{input_port.consuming_abstract_data_product_id}."
                        )
                        input_port.expired_on = now
                        input_port.status = DecisionStatus.PENDING
                    else:
                        raise InvalidInputPortState(
                            f"The {input_port.id} has is_renewing {input_port.is_renewing} and "
                            f"{input_port.dataset.access_type} which is impossible since it "
                            "should have been auto-approved."
                        )

                db.commit()
        except Exception as e:
            logger.warning(f"[InputPort Expiry] Expiry check failed: {e}")
        await asyncio.sleep(INPUT_PORT_EXPIRY_CHECK_INTERVAL_SECONDS)
