from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import InputPort
from app.core.context import close_event_context, open_event_context, pop_events
from app.core.webhooks.events import InputPortEvent, InputPortExpiredEvent
from tests import test_session
from tests.factories import InputPortFactory

TODAY = date.today()


def _recompute_and_collect_events(link_id):
    token = open_event_context()
    link = (
        test_session.execute(
            select(InputPort)
            .where(InputPort.id == link_id)
            .options(selectinload(InputPort.requests))
        )
        .scalars()
        .unique()
        .one()
    )
    link.recompute_status()
    test_session.commit()
    events = pop_events()
    close_event_context(token)
    return link, events


class TestInputPortExpiredEvent:
    def test_generate_extra_events__transition_to_expired_emits_expired_event(self):
        link = InputPortFactory(
            status=InputPortStatus.APPROVED,
            request__valid_until=TODAY - timedelta(days=1),
            request__decided_by=None,
        )
        test_session.commit()

        link, events = _recompute_and_collect_events(link.id)

        assert link.status == InputPortStatus.EXPIRED
        event_types = {type(event) for event in events}
        assert event_types == {InputPortEvent, InputPortExpiredEvent}

    def test_generate_extra_events__staying_approved_emits_nothing(self):
        link = InputPortFactory(
            status=InputPortStatus.APPROVED,
            request__valid_until=TODAY + timedelta(days=10),
            request__decided_by=None,
        )
        test_session.commit()

        link, events = _recompute_and_collect_events(link.id)

        assert link.status == InputPortStatus.APPROVED
        assert events == []

    def test_generate_extra_events__already_expired_recheck_emits_nothing(self):
        link = InputPortFactory(
            status=InputPortStatus.EXPIRED,
            request__valid_until=TODAY - timedelta(days=1),
            request__decided_by=None,
        )
        test_session.commit()

        link, events = _recompute_and_collect_events(link.id)

        assert link.status == InputPortStatus.EXPIRED
        assert events == []
