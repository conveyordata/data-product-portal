from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.abstract_data_product.input_ports.enums import (
    InputPortRequestDecision,
    InputPortStatus,
)
from app.abstract_data_product.input_ports.model import (
    InputPortRequest as InputPortRequestModel,
)
from app.access_durations.enums import AccessDurationType
from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.input_ports.service import InputPortService
from app.settings import settings
from tests import test_session
from tests.factories import (
    DataProductFactory,
    InputPortFactory,
    InputPortRequestFactory,
    OutputPortFactory,
    UserFactory,
)


def _grant_and_pending_renewal(consumer, port):
    link = InputPortFactory(
        consuming_abstract_data_product=consumer,
        output_port=port,
        status=DecisionStatus.APPROVED,
        request__access_duration_type=AccessDurationType.TIME_BOUND,
        request__requested_duration_days=30,
        request__valid_from=date.today() - timedelta(days=5),
        request__valid_until=date.today() + timedelta(days=10),
    )
    grant = test_session.scalars(
        select(InputPortRequestModel).where(
            InputPortRequestModel.input_port_id == link.id
        )
    ).one()
    renewal = InputPortRequestFactory(
        input_port=link,
        decision=InputPortRequestDecision.PENDING,
        access_duration_type=AccessDurationType.TIME_BOUND,
        requested_duration_days=30,
        decided_by=None,
    )
    test_session.commit()
    return link, grant, renewal


class TestInputPortService:
    def test_get_user_requests(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        now = datetime.now(timezone.utc)
        pending_recent = InputPortRequestFactory(
            requested_by=user,
            requested_on=now - timedelta(days=1),
            created_on=now - timedelta(days=1),
            decision=InputPortRequestDecision.PENDING,
        )
        pending_old = InputPortRequestFactory(
            requested_by=user,
            requested_on=now - timedelta(days=60),
            created_on=now - timedelta(days=60),
            decision=InputPortRequestDecision.PENDING,
        )
        approved_old = InputPortRequestFactory(
            requested_by=user,
            requested_on=now - timedelta(days=60),
            created_on=now - timedelta(days=60),
            decision=InputPortRequestDecision.APPROVED,
        )
        requests_old_inactive_hidden = InputPortService(session).get_user_requests(
            user, True
        )
        requests_all = InputPortService(session).get_user_requests(user, False)
        assert len(requests_old_inactive_hidden) == 2
        assert len(requests_all) == 3
        requests_old_inactive_hidden_ids = [r.id for r in requests_old_inactive_hidden]
        assert pending_recent.id in requests_old_inactive_hidden_ids
        assert pending_old.id in requests_old_inactive_hidden_ids
        assert approved_old.id not in requests_old_inactive_hidden_ids


def _by_id(link):
    return {request.id: request for request in link.requests}


class TestInputPortDecisions:
    def test_approve__renewal_window_starts_at_current_date(self):
        actor = UserFactory()
        consumer = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.RESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        link, grant, renewal = _grant_and_pending_renewal(consumer, port)

        current_link = InputPortService(test_session).approve_output_port_as_input_port(
            data_product_id=port.data_product.id,
            output_port_id=port.id,
            consuming_data_product_id=consumer.id,
            actor=actor,
        )

        requests = _by_id(current_link)
        assert current_link.status == InputPortStatus.APPROVED
        assert requests[renewal.id].decision == InputPortRequestDecision.APPROVED
        assert requests[grant.id].valid_until == date.today() + timedelta(days=10)
        assert current_link.active_grant.id == renewal.id
        assert requests[renewal.id].valid_from == date.today()
        assert requests[renewal.id].valid_until == date.today() + (timedelta(days=30))

    def test_deny__pending_renewal_keeps_the_active_grant(self):
        actor = UserFactory()
        consumer = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.RESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        link, grant, renewal = _grant_and_pending_renewal(consumer, port)

        current_link = InputPortService(test_session).deny_output_port_as_input_port(
            data_product_id=port.data_product.id,
            output_port_id=port.id,
            consuming_data_product_id=consumer.id,
            actor=actor,
            decision_note="not now",
        )

        requests = _by_id(current_link)
        assert requests[renewal.id].decision == InputPortRequestDecision.DENIED
        assert requests[grant.id].valid_until == date.today() + timedelta(days=10)
        assert current_link.status == InputPortStatus.APPROVED

    def test_deny__raises_when_only_an_active_grant_exists(self):
        actor = UserFactory()
        consumer = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.RESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        InputPortFactory(
            consuming_abstract_data_product=consumer,
            output_port=port,
            status=DecisionStatus.APPROVED,
            request__access_duration_type=AccessDurationType.TIME_BOUND,
            request__requested_duration_days=30,
            request__valid_from=date.today() - timedelta(days=5),
            request__valid_until=date.today() + timedelta(days=10),
        )
        test_session.commit()

        with pytest.raises(HTTPException) as exc:
            InputPortService(test_session).deny_output_port_as_input_port(
                data_product_id=port.data_product.id,
                output_port_id=port.id,
                consuming_data_product_id=consumer.id,
                actor=actor,
                decision_note="not now",
            )
        assert exc.value.status_code == 400

    def test_revoke__revokes_the_active_grant(self):
        actor = UserFactory()
        consumer = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.RESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        link = InputPortFactory(
            consuming_abstract_data_product=consumer,
            output_port=port,
            status=DecisionStatus.APPROVED,
            request__access_duration_type=AccessDurationType.TIME_BOUND,
            request__requested_duration_days=30,
            request__valid_from=date.today() - timedelta(days=5),
            request__valid_until=date.today() + timedelta(days=10),
        )
        grant = test_session.scalars(
            select(InputPortRequestModel).where(
                InputPortRequestModel.input_port_id == link.id
            )
        ).one()
        test_session.commit()

        current_link = InputPortService(test_session).revoke_output_port_as_input_port(
            data_product_id=port.data_product.id,
            output_port_id=port.id,
            consuming_data_product_id=consumer.id,
            actor=actor,
        )
        test_session.flush()

        requests = _by_id(current_link)
        assert current_link.status == InputPortStatus.REVOKED
        assert requests[grant.id].revoked_at is not None
        assert requests[grant.id].revoked_by_id == actor.id
        assert requests[grant.id].decision == InputPortRequestDecision.APPROVED

    def test_revoke__raises_when_no_active_grant(self):
        actor = UserFactory()
        consumer = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        InputPortFactory(
            consuming_abstract_data_product=consumer,
            output_port=port,
            status=DecisionStatus.PENDING,
        )
        test_session.commit()

        with pytest.raises(HTTPException) as exc:
            InputPortService(test_session).revoke_output_port_as_input_port(
                data_product_id=port.data_product.id,
                output_port_id=port.id,
                consuming_data_product_id=consumer.id,
                actor=actor,
            )
        assert exc.value.status_code == 400

    def test_approve__renewal_after_expiry_starts_today(self):
        actor = UserFactory()
        consumer = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.RESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        link = InputPortFactory(
            consuming_abstract_data_product=consumer,
            output_port=port,
            status=DecisionStatus.APPROVED,
            request__access_duration_type=AccessDurationType.TIME_BOUND,
            request__requested_duration_days=30,
            request__valid_from=date.today() - timedelta(days=40),
            request__valid_until=date.today() - timedelta(days=5),
        )
        link.expiry_event_sent = True
        renewal = InputPortRequestFactory(
            input_port=link,
            decision=InputPortRequestDecision.PENDING,
            access_duration_type=AccessDurationType.TIME_BOUND,
            requested_duration_days=30,
            decided_by=None,
        )
        test_session.commit()

        current_link = InputPortService(test_session).approve_output_port_as_input_port(
            data_product_id=port.data_product.id,
            output_port_id=port.id,
            consuming_data_product_id=consumer.id,
            actor=actor,
        )

        requests = _by_id(current_link)
        assert requests[renewal.id].valid_from == date.today()
        assert requests[renewal.id].valid_until == date.today() + timedelta(days=30)
        assert current_link.expiry_event_sent is False
