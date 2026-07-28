import asyncio
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

from app.abstract_data_product.input_ports.background_tasks import expire_input_ports
from app.abstract_data_product.input_ports.enums import InputPortStatus
from tests import test_session
from tests.factories import InputPortFactory

TODAY = date.today()


def _mock_emit():
    return patch(
        "app.abstract_data_product.input_ports.background_tasks.emit_all_events",
        AsyncMock(),
    )


class TestExpireInputPorts:
    def test_expire_input_ports__lapsed_grant_flips_to_expired_and_sends_event(self):
        link = InputPortFactory(
            status=InputPortStatus.APPROVED,
            request__valid_until=TODAY - timedelta(days=1),
            request__decided_by=None,
        )
        test_session.commit()

        with _mock_emit() as mock_emit:
            asyncio.run(expire_input_ports(test_session))

        test_session.refresh(link)
        assert link.status == InputPortStatus.EXPIRED
        mock_emit.assert_awaited_once()
        (events,) = mock_emit.call_args.args
        event_types = {event.event_type() for event in events}
        assert event_types == {"input_port.event", "input_port.expired"}
        assert all(event.id == link.id for event in events)

    def test_expire_input_ports__active_grant_is_untouched(self):
        link = InputPortFactory(
            status=InputPortStatus.APPROVED,
            request__valid_until=TODAY + timedelta(days=10),
            request__decided_by=None,
        )
        test_session.commit()

        with _mock_emit() as mock_emit:
            asyncio.run(expire_input_ports(test_session))

        test_session.refresh(link)
        assert link.status == InputPortStatus.APPROVED
        mock_emit.assert_awaited_once_with([])

    def test_expire_input_ports__already_expired_link_sends_nothing(self):
        link = InputPortFactory(
            status=InputPortStatus.EXPIRED,
            request__valid_until=TODAY - timedelta(days=1),
            request__decided_by=None,
        )
        test_session.commit()

        with _mock_emit() as mock_emit:
            asyncio.run(expire_input_ports(test_session))

        test_session.refresh(link)
        assert link.status == InputPortStatus.EXPIRED
        mock_emit.assert_awaited_once_with([])

    def test_expire_input_ports__pending_only_link_is_ignored(self):
        link = InputPortFactory(status=InputPortStatus.PENDING)
        test_session.commit()

        with _mock_emit() as mock_emit:
            asyncio.run(expire_input_ports(test_session))

        test_session.refresh(link)
        assert link.status == InputPortStatus.PENDING
        mock_emit.assert_awaited_once_with([])
