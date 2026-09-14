import asyncio
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.abstract_data_product.input_ports.enums import InputPortStatus, RenewalStatus
from app.abstract_data_product.input_ports.model import InputPort
from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.core.context import close_event_context, open_event_context, pop_events
from app.core.logging import logger
from app.core.webhooks.v2 import emit_all_events
from app.database.database import SessionLocal
from app.events.enums import EventReferenceEntity, EventType
from app.settings import settings

CHECK_INTERVAL_SECONDS = 24 * 60 * 60


def _is_expiring_soon(input_port: InputPort) -> bool:
    active_grant = input_port.active_grant
    if (
        input_port.status != InputPortStatus.APPROVED
        or active_grant is None
        or active_grant.valid_until is None
        or input_port.renewal_status == RenewalStatus.PENDING
    ):
        return False
    days_until_expiry = (active_grant.valid_until - date.today()).days
    return 0 <= days_until_expiry <= settings.EXPIRING_SOON_THRESHOLD_DAYS


def _get_system_actor_id(db: Session):
    from app.users.model import User

    return db.scalar(
        select(User.id).where(User.external_id == SYSTEM_ACCOUNT_BOT_EXTERNAL_ID)
    )


def _was_expiring_soon_notification_sent(db: Session, input_port: InputPort) -> bool:
    from app.events.model import Event as EventModel

    active_grant = input_port.active_grant
    if active_grant is None:
        return False
    return (
        db.scalar(
            select(EventModel.id)
            .where(
                EventModel.name == EventType.DATA_PRODUCT_DATASET_LINK_EXPIRING_SOON,
                EventModel.subject_id == input_port.output_port_id,
                EventModel.subject_type == EventReferenceEntity.DATASET,
                EventModel.target_id == input_port.consuming_abstract_data_product_id,
                EventModel.target_type == EventReferenceEntity.DATA_PRODUCT,
                EventModel.created_on >= active_grant.requested_on,
            )
            .limit(1)
        )
        is not None
    )


def _create_expiring_soon_notification(
    db: Session, input_port: InputPort, system_actor_id
) -> None:
    from app.events.schema import CreateEvent
    from app.events.service import EventService
    from app.users.notifications.service import NotificationService

    active_grant = input_port.active_grant
    if active_grant is None or _was_expiring_soon_notification_sent(db, input_port):
        return
    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_EXPIRING_SOON,
            subject_id=input_port.output_port_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=input_port.consuming_abstract_data_product_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=system_actor_id,
        )
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=input_port.consuming_abstract_data_product_id,
        event_id=event_id,
        extra_receiver_ids=[active_grant.requested_by_id],
    )
    logger.info(
        f"[InputPort Expiry] Sent expiring soon notification for input port {input_port.id} "
        f"for consuming data product {input_port.consuming_abstract_data_product_id}"
    )


async def expire_input_ports(db: Session) -> None:
    token = open_event_context()
    try:
        system_actor_id = _get_system_actor_id(db)
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
            if _is_expiring_soon(input_port):
                if system_actor_id is None:
                    logger.warning(
                        "[InputPort Expiry] Could not send expiring soon notifications because the system account is missing"
                    )
                else:
                    _create_expiring_soon_notification(db, input_port, system_actor_id)
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
