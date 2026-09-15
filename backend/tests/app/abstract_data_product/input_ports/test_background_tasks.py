import asyncio
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

from sqlalchemy import select

from app.abstract_data_product.input_ports.background_tasks import expire_input_ports
from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.events.enums import EventReferenceEntity, EventType
from app.events.model import Event
from app.users.notifications.model import Notification
from tests.factories import (
    DataProductRoleAssignmentFactory,
    InputPortFactory,
    RoleFactory,
    UserFactory,
)

TODAY = date.today()


def _mock_emit():
    return patch(
        "app.abstract_data_product.input_ports.background_tasks.emit_all_events",
        AsyncMock(),
    )


class TestExpireInputPorts:
    def test_expire_input_ports__lapsed_grant_flips_to_expired_and_sends_event(
        self, session
    ):
        link = InputPortFactory(
            status=InputPortStatus.APPROVED,
            request__valid_until=TODAY - timedelta(days=1),
            request__decided_by=None,
        )

        with _mock_emit() as mock_emit:
            asyncio.run(expire_input_ports(session))

        session.refresh(link)
        assert link.status == InputPortStatus.EXPIRED
        mock_emit.assert_awaited_once()
        (events,) = mock_emit.call_args.args
        assert len(events) == 1
        assert events[0].event_type() == "input_port.event"
        assert events[0].id == link.id

    def test_expire_input_ports__active_grant_is_untouched(self, session):
        link = InputPortFactory(
            status=InputPortStatus.APPROVED,
            request__valid_until=TODAY + timedelta(days=20),
            request__decided_by=None,
        )

        with _mock_emit() as mock_emit:
            asyncio.run(expire_input_ports(session))

        session.refresh(link)
        assert link.status == InputPortStatus.APPROVED
        mock_emit.assert_awaited_once_with([])

    def test_expire_input_ports__already_expired_link_sends_nothing(self, session):
        link = InputPortFactory(
            status=InputPortStatus.EXPIRED,
            request__valid_until=TODAY - timedelta(days=1),
            request__decided_by=None,
        )

        with _mock_emit() as mock_emit:
            asyncio.run(expire_input_ports(session))

        session.refresh(link)
        assert link.status == InputPortStatus.EXPIRED
        mock_emit.assert_awaited_once_with([])

    def test_expire_input_ports__pending_only_link_is_ignored(self, session):
        link = InputPortFactory(status=InputPortStatus.PENDING)

        with _mock_emit() as mock_emit:
            asyncio.run(expire_input_ports(session))

        session.refresh(link)
        assert link.status == InputPortStatus.PENDING
        mock_emit.assert_awaited_once_with([])

    def test_expire_input_ports__expiring_soon_grant_creates_consumer_notifications_once(
        self, session
    ):
        system_user = UserFactory(external_id=SYSTEM_ACCOUNT_BOT_EXTERNAL_ID)
        requester = UserFactory()
        consumer = UserFactory()
        link = InputPortFactory(
            status=InputPortStatus.APPROVED,
            request__requested_by=requester,
            request__valid_until=TODAY + timedelta(days=10),
            request__decided_by=None,
        )
        DataProductRoleAssignmentFactory(
            data_product_id=link.consuming_abstract_data_product_id,
            user_id=consumer.id,
            role_id=RoleFactory().id,
        )

        with _mock_emit():
            asyncio.run(expire_input_ports(session))
            asyncio.run(expire_input_ports(session))

        notifications = session.scalars(select(Notification)).all()
        assert {notification.user_id for notification in notifications} == {
            requester.id,
            consumer.id,
        }
        events = session.scalars(
            select(Event).where(
                Event.name == EventType.DATA_PRODUCT_DATASET_LINK_EXPIRING_SOON
            )
        ).all()
        assert len(events) == 1
        assert events[0].actor_id == system_user.id
        assert events[0].subject_id == link.output_port_id
        assert events[0].subject_type == EventReferenceEntity.DATASET
        assert events[0].target_id == link.consuming_abstract_data_product_id
        assert events[0].target_type == EventReferenceEntity.DATA_PRODUCT
