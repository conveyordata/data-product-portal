import asyncio

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import InputPort
from app.core.context import close_event_context, open_event_context, pop_events
from app.core.logging import logger
from app.core.webhooks.v2 import emit_all_events
from app.database.database import SessionLocal

CHECK_INTERVAL_SECONDS = 24 * 60 * 60


async def expire_input_ports(db: Session) -> None:
    token = open_event_context()
    events = []
    try:
        candidates = (
            db.execute(
                select(InputPort)
                .where(InputPort.status == InputPortStatus.APPROVED)
                .options(selectinload(InputPort.requests))
            )
            .scalars()
            .unique()
            .all()
        )
        for input_port in candidates:
            input_port.recompute_status()
            if input_port.status == InputPortStatus.EXPIRED:
                events.append(input_port.to_event())
                logger.info(
                    f"[InputPort Expiry] Expired input port {input_port.id} "
                    f"for consuming data product {input_port.consuming_abstract_data_product_id}"
                )
        db.commit()
    finally:
        pop_events()
        close_event_context(token)
    await emit_all_events(events)


async def expire_input_ports_task() -> None:
    while True:
        try:
            with SessionLocal() as db:
                await expire_input_ports(db)
        except Exception as e:
            logger.warning(f"[InputPort Expiry] Expiry check failed: {e}")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
