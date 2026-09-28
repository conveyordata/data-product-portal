import asyncio

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import InputPort
from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.core.context import close_event_context, open_event_context, pop_events
from app.core.logging import logger
from app.core.webhooks.v2 import emit_all_events
from app.database.database import SessionLocal

CHECK_INTERVAL_SECONDS = 24 * 60 * 60
EXPIRY_LOCK_KEY = 4300


async def expire_input_ports(db: Session) -> None:
    from app.data_products.output_ports.input_ports.service import InputPortService
    from app.users.model import User

    token = open_event_context()
    try:
        if not db.scalar(select(func.pg_try_advisory_xact_lock(EXPIRY_LOCK_KEY))):
            logger.info("[InputPort Expiry] Skipped, another instance is running")
            return
        system_actor_id = db.scalar(
            select(User.id).where(User.external_id == SYSTEM_ACCOUNT_BOT_EXTERNAL_ID)
        )
        if system_actor_id is None:
            logger.warning(
                "[InputPort Expiry] Could not send expiring soon notifications because the system account is missing"
            )
        service = InputPortService(db)
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
            if system_actor_id and service.notify_if_expiring_soon(
                input_port, system_actor_id
            ):
                logger.info(
                    f"[InputPort Expiry] Sent expiring soon notification for input port {input_port.id} "
                    f"for consuming data product {input_port.consuming_abstract_data_product_id}"
                )
            input_port.recompute_status()
            if input_port.status == InputPortStatus.EXPIRED:
                logger.info(
                    f"[InputPort Expiry] Expired input port {input_port.id} "
                    f"for consuming data product {input_port.consuming_abstract_data_product_id}"
                )
        db.commit()
        events = pop_events()
    finally:
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
