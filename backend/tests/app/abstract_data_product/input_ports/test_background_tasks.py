import asyncio
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

from app.abstract_data_product.input_ports.background_tasks import expire_input_ports
from app.abstract_data_product.input_ports.enums import InputPortStatus
from tests import test_session
from tests.factories import InputPortFactory

TODAY = date.today()


def _mock_webhook(result: bool):
    return patch(
        "app.abstract_data_product.input_ports.background_tasks.call_v2_webhook",
        AsyncMock(return_value=result),
    )


class TestExpireInputPorts:
    def test_expire_input_ports__lapsed_grant_flips_to_expired_and_sends_event(self):
        link = InputPortFactory(
            status=InputPortStatus.APPROVED,
            request__valid_until=TODAY - timedelta(days=1),
            request__decided_by=None,
        )
        test_session.commit()

        with _mock_webhook(True) as mock_webhook:
            asyncio.run(expire_input_ports(test_session))

        test_session.refresh(link)
        assert link.status == InputPortStatus.EXPIRED
        assert link.expiry_event_sent is True
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "input_port.event"
        assert data["id"] == str(link.id)

    def test_expire_input_ports__active_grant_is_untouched(self):
        link = InputPortFactory(
            status=InputPortStatus.APPROVED,
            request__valid_until=TODAY + timedelta(days=10),
            request__decided_by=None,
        )
        test_session.commit()

        with _mock_webhook(True) as mock_webhook:
            asyncio.run(expire_input_ports(test_session))

        test_session.refresh(link)
        assert link.status == InputPortStatus.APPROVED
        assert link.expiry_event_sent is False
        mock_webhook.assert_not_awaited()

    def test_expire_input_ports__failed_delivery_keeps_flag_unset_for_retry(self):
        link = InputPortFactory(
            status=InputPortStatus.APPROVED,
            request__valid_until=TODAY - timedelta(days=1),
            request__decided_by=None,
        )
        test_session.commit()

        with _mock_webhook(False):
            asyncio.run(expire_input_ports(test_session))

        test_session.refresh(link)
        assert link.status == InputPortStatus.EXPIRED
        assert link.expiry_event_sent is False

    def test_expire_input_ports__already_sent_is_not_resent(self):
        link = InputPortFactory(
            status=InputPortStatus.EXPIRED,
            request__valid_until=TODAY - timedelta(days=1),
            request__decided_by=None,
        )
        link.expiry_event_sent = True
        test_session.commit()

        with _mock_webhook(True) as mock_webhook:
            asyncio.run(expire_input_ports(test_session))

        mock_webhook.assert_not_awaited()

    def test_expire_input_ports__pending_only_link_is_ignored(self):
        link = InputPortFactory(status=InputPortStatus.PENDING)
        test_session.commit()

        with _mock_webhook(True) as mock_webhook:
            asyncio.run(expire_input_ports(test_session))

        test_session.refresh(link)
        assert link.status == InputPortStatus.PENDING
        mock_webhook.assert_not_awaited()
