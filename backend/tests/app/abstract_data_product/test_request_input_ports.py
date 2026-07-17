from datetime import date, datetime, timedelta

import pytest
import pytz
from fastapi import HTTPException
from sqlalchemy import select

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import InputPortRequest
from app.abstract_data_product.service import AbstractDataProductService
from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_ports.enums import OutputPortAccessType
from tests import test_session
from tests.factories import (
    AccessDurationFactory,
    DataProductFactory,
    ExplorationFactory,
    InputPortFactory,
    OutputPortFactory,
    UserFactory,
)


def _requests_for(input_port_id):
    return test_session.scalars(
        select(InputPortRequest).where(InputPortRequest.input_port_id == input_port_id)
    ).all()


def _request_for(input_port):
    return test_session.scalars(
        select(InputPortRequest).where(InputPortRequest.input_port_id == input_port.id)
    ).one()


class TestRequestInputPortsDuration:
    def test_request_input_ports__time_bound_data_product_port_sets_window(self):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
        )

        [ip] = AbstractDataProductService(test_session).request_input_ports(
            dp.id, [port.id], "need access", actor=actor
        )

        req = _request_for(ip)
        assert req.access_duration_type == AccessDurationType.TIME_BOUND
        assert req.requested_duration_days == 30
        assert req.valid_until == datetime.now(pytz.utc).date() + timedelta(days=30)

    def test_request_input_ports__permanent_port_has_no_window(self):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.UNRESTRICTED)

        [ip] = AbstractDataProductService(test_session).request_input_ports(
            dp.id, [port.id], "need access", actor=actor
        )

        req = _request_for(ip)
        assert req.access_duration_type == AccessDurationType.PERMANENT
        assert req.requested_duration_days is None
        assert req.valid_until is None

    def test_request_input_ports__exploration_uses_exploration_duration_type(self):
        actor = UserFactory()
        exploration = ExplorationFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
            exploration_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.EXPLORATION,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=15,
        )

        [ip] = AbstractDataProductService(test_session).request_input_ports(
            exploration.id, [port.id], "need access", actor=actor
        )

        req = _request_for(ip)
        assert req.access_duration_type == AccessDurationType.TIME_BOUND
        assert req.requested_duration_days == 15

    def test_request_input_ports__time_bound_without_policy_row_errors(self):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(test_session).request_input_ports(
                dp.id, [port.id], "need access", actor=actor
            )
        assert exc.value.status_code == 500


class TestRequestInputPortsRenewal:
    def _restricted_time_bound_port(self):
        port = OutputPortFactory(
            access_type=OutputPortAccessType.RESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
        )
        return port

    def test_request_input_ports__renewal_on_active_grant_creates_pending_request(
        self,
    ):
        actor = UserFactory()
        dp = DataProductFactory()
        port = self._restricted_time_bound_port()
        link = InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.APPROVED,
            request__access_duration_type=AccessDurationType.TIME_BOUND,
            request__requested_duration_days=30,
            request__valid_until=date.today() + timedelta(days=10),
        )

        [ip] = AbstractDataProductService(test_session).request_input_ports(
            dp.id, [port.id], "renew please", actor=actor
        )

        assert ip.id == link.id
        reqs = _requests_for(link.id)
        assert len(reqs) == 2
        assert sum(r.decision == DecisionStatus.PENDING for r in reqs) == 1
        test_session.refresh(link)
        assert link.status == InputPortStatus.APPROVED

    def test_request_input_ports__renewal_reuses_previous_justification(self):
        actor = UserFactory()
        dp = DataProductFactory()
        port = self._restricted_time_bound_port()
        link = InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.APPROVED,
            request__justification="original reason",
            request__access_duration_type=AccessDurationType.TIME_BOUND,
            request__requested_duration_days=30,
            request__valid_until=date.today() + timedelta(days=10),
        )

        AbstractDataProductService(test_session).request_input_ports(
            dp.id, [port.id], "a different body justification", actor=actor
        )

        reqs = _requests_for(link.id)
        renewal = next(r for r in reqs if r.decision == DecisionStatus.PENDING)
        assert renewal.justification == "original reason"

    def test_request_input_ports__blocked_when_a_request_is_already_pending(self):
        actor = UserFactory()
        dp = DataProductFactory()
        port = self._restricted_time_bound_port()
        link = InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.PENDING,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(test_session).request_input_ports(
                dp.id, [port.id], "again", actor=actor
            )
        assert exc.value.status_code == 400
        assert len(_requests_for(link.id)) == 1

    def test_request_input_ports__blocked_when_active_grant_is_permanent(self):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.APPROVED,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(test_session).request_input_ports(
                dp.id, [port.id], "renew", actor=actor
            )
        assert exc.value.status_code == 400

    def test_request_input_ports__re_request_allowed_on_denied_link(self):
        actor = UserFactory()
        dp = DataProductFactory()
        port = self._restricted_time_bound_port()
        link = InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.DENIED,
        )

        [ip] = AbstractDataProductService(test_session).request_input_ports(
            dp.id, [port.id], "retry", actor=actor
        )

        assert ip.id == link.id
        assert len(_requests_for(link.id)) == 2
