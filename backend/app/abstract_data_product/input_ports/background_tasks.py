import asyncio

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import InputPort
from app.core.context import close_event_context, open_event_context, pop_events
from app.core.logging import logger
from app.core.webhooks.v2 import call_v2_webhook
from app.database.database import SessionLocal

CHECK_INTERVAL_SECONDS = 86400


async def expire_input_ports(db: Session) -> None:
    token = open_event_context()
    try:
        candidates = (
            db.execute(
                select(InputPort)
                .where(
                    InputPort.status.in_(
                        (InputPortStatus.APPROVED, InputPortStatus.EXPIRED)
                    )
                )
                .where(InputPort.expiry_event_sent.is_(False))
                .options(selectinload(InputPort.requests))
            )
            .scalars()
            .unique()
            .all()
        )
        for input_port in candidates:
            input_port.recompute_status()
            if input_port.status != InputPortStatus.EXPIRED:
                continue

            event = input_port.to_event()
            if await call_v2_webhook(
                type(event).event_type(), event.model_dump(mode="json")
            ):
                input_port.expiry_event_sent = True
                logger.info(
                    f"[InputPort Expiry] Expired input port {input_port.id} "
                    f"for consuming data product {input_port.consuming_abstract_data_product_id}"
                )
            else:
                logger.warning(
                    f"[InputPort Expiry] Failed to deliver access-ended event for "
                    f"input port {input_port.id}; will retry on the next run"
                )
        db.commit()
    finally:
        pop_events()
        close_event_context(token)


async def expire_input_ports_task() -> None:
    while True:
        try:
            with SessionLocal() as db:
                await expire_input_ports(db)
        except Exception as e:
            logger.warning(f"[InputPort Expiry] Expiry check failed: {e}")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
