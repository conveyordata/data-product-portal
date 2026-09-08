import uuid
from datetime import date, datetime, timedelta

import pytest
import pytz
from fastapi import HTTPException
from sqlalchemy import select

from app.abstract_data_product.input_ports.enums import (
    InputPortRequestDecision,
    InputPortStatus,
)
from app.abstract_data_product.input_ports.model import InputPortRequest
from app.abstract_data_product.schema_request import (
    RequestInputPortsForAbstractDataProductRequestItem,
)
from app.abstract_data_product.service import AbstractDataProductService
from app.abstract_data_product.type import AbstractDataProductType
from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.access_durations.enums import AccessDurationType
from app.data_products.output_ports.enums import OutputPortAccessType
from tests.factories import (
    AccessDurationFactory,
    AccessModeFactory,
    DataProductFactory,
    ExplorationFactory,
    InputPortFactory,
    OutputPortFactory,
    TechnicalAssetFactory,
    TechnicalAssetOutputPortAssociationFactory,
    UserFactory,
)


def _requests_for(input_port_id, session):
    return session.scalars(
        select(InputPortRequest).where(InputPortRequest.input_port_id == input_port_id)
    ).all()


def _request_for(input_port, session):
    return session.scalars(
        select(InputPortRequest).where(InputPortRequest.input_port_id == input_port.id)
    ).one()


class TestRequestInputPortsDuration:
    def test_request_input_ports__time_bound_data_product_port_sets_window(
        self, session
    ):
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

        [ip] = AbstractDataProductService(session).request_input_ports(
            dp.id,
            [
                RequestInputPortsForAbstractDataProductRequestItem(
                    output_port_id=port.id
                )
            ],
            "need access",
            actor=actor,
        )

        req = _request_for(ip, session)
        assert req.access_duration_type == AccessDurationType.TIME_BOUND
        assert req.requested_duration_days == 30
        assert req.valid_until == datetime.now(pytz.utc).date() + timedelta(days=30)

    def test_request_input_ports__permanent_port_has_no_window(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.UNRESTRICTED)

        [ip] = AbstractDataProductService(session).request_input_ports(
            dp.id,
            [
                RequestInputPortsForAbstractDataProductRequestItem(
                    output_port_id=port.id
                )
            ],
            "need access",
            actor=actor,
        )

        req = _request_for(ip, session)
        assert req.access_duration_type == AccessDurationType.PERMANENT
        assert req.requested_duration_days is None
        assert req.valid_until is None

    def test_request_input_ports__exploration_uses_exploration_duration_type(
        self, session
    ):
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

        [ip] = AbstractDataProductService(session).request_input_ports(
            exploration.id,
            [
                RequestInputPortsForAbstractDataProductRequestItem(
                    output_port_id=port.id
                )
            ],
            "need access",
            actor=actor,
        )

        req = _request_for(ip, session)
        assert req.access_duration_type == AccessDurationType.TIME_BOUND
        assert req.requested_duration_days == 15

    def test_request_input_ports__time_bound_without_policy_row_errors(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).request_input_ports(
                dp.id,
                [
                    RequestInputPortsForAbstractDataProductRequestItem(
                        output_port_id=port.id
                    )
                ],
                "need access",
                actor=actor,
            )
        assert exc.value.status_code == 500

    @pytest.mark.parametrize(
        "status",
        [DecisionStatus.PENDING, DecisionStatus.APPROVED, DecisionStatus.DENIED],
    )
    def test_request_input_ports__fails_when_link_already_exists(self, status, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        link = InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=status,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).request_input_ports(
                dp.id,
                [
                    RequestInputPortsForAbstractDataProductRequestItem(
                        output_port_id=port.id
                    )
                ],
                "again",
                actor=actor,
            )
        assert exc.value.status_code == 400
        assert len(_requests_for(link.id, session)) == 1

    def test_request_input_ports__access_mode(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
        )
        access_mode = AccessModeFactory(name="a name")
        TechnicalAssetOutputPortAssociationFactory(
            data_output=TechnicalAssetFactory(access_modes=[access_mode]),
            output_port=port,
        )

        [ip] = AbstractDataProductService(session).request_input_ports(
            dp.id,
            [
                RequestInputPortsForAbstractDataProductRequestItem(
                    output_port_id=port.id, access_mode_id=access_mode.id
                )
            ],
            "need access",
            actor=actor,
        )
        assert ip.latest_request.access_mode_id == access_mode.id

    def test_request_input_ports__access_mode_required(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
        )
        TechnicalAssetOutputPortAssociationFactory(
            data_output=TechnicalAssetFactory(
                access_modes=[AccessModeFactory(name="a name")]
            ),
            output_port=port,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).request_input_ports(
                dp.id,
                [
                    RequestInputPortsForAbstractDataProductRequestItem(
                        output_port_id=port.id
                    )
                ],
                "need access",
                actor=actor,
            )

        assert exc.value.status_code == 400

    def test_request_input_ports__access_mode_does_not_exist(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
        )
        TechnicalAssetOutputPortAssociationFactory(
            data_output=TechnicalAssetFactory(
                access_modes=[AccessModeFactory(name="a name")]
            ),
            output_port=port,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).request_input_ports(
                dp.id,
                [
                    RequestInputPortsForAbstractDataProductRequestItem(
                        output_port_id=port.id, access_mode_id=uuid.uuid4()
                    )
                ],
                "need access",
                actor=actor,
            )

        assert exc.value.status_code == 400

    def test_request_input_ports__access_mode_from_any_linked_technical_asset(
        self, session
    ):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
        )
        denied_mode = AccessModeFactory(name="denied mode")
        approved_mode = AccessModeFactory(name="approved mode")
        TechnicalAssetOutputPortAssociationFactory(
            data_output=TechnicalAssetFactory(access_modes=[denied_mode]),
            output_port=port,
            status=DecisionStatus.DENIED,
        )
        TechnicalAssetOutputPortAssociationFactory(
            data_output=TechnicalAssetFactory(access_modes=[approved_mode]),
            output_port=port,
            status=DecisionStatus.APPROVED,
        )

        [ip] = AbstractDataProductService(session).request_input_ports(
            dp.id,
            [
                RequestInputPortsForAbstractDataProductRequestItem(
                    output_port_id=port.id, access_mode_id=approved_mode.id
                )
            ],
            "need access",
            actor=actor,
        )

        assert ip.latest_request.access_mode_id == approved_mode.id

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

    def test_renew_input_port__on_active_grant_creates_pending_request(self, session):
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

        ip = AbstractDataProductService(session).renew_input_port(
            dp.id, port.id, actor=actor
        )

        assert ip.id == link.id
        reqs = _requests_for(link.id, session)
        assert len(reqs) == 2
        assert sum(r.decision == InputPortRequestDecision.PENDING for r in reqs) == 1
        session.refresh(link)
        assert link.status == InputPortStatus.APPROVED

    def test_renew_input_port__reuses_previous_justification(self, session):
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

        AbstractDataProductService(session).renew_input_port(
            dp.id, port.id, actor=actor
        )

        reqs = _requests_for(link.id, session)
        renewal = next(
            r for r in reqs if r.decision == InputPortRequestDecision.PENDING
        )
        assert renewal.justification == "original reason"

    def test_renew_input_port__blocked_when_a_request_is_already_pending(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = self._restricted_time_bound_port()
        link = InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.PENDING,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).renew_input_port(
                dp.id, port.id, actor=actor
            )
        assert exc.value.status_code == 400
        assert len(_requests_for(link.id, session)) == 1

    def test_renew_input_port__blocked_when_active_grant_is_permanent(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.APPROVED,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).renew_input_port(
                dp.id, port.id, actor=actor
            )
        assert exc.value.status_code == 400

    def test_renew_input_port__allowed_on_denied_link(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = self._restricted_time_bound_port()
        link = InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.DENIED,
        )

        ip = AbstractDataProductService(session).renew_input_port(
            dp.id, port.id, actor=actor
        )

        assert ip.id == link.id
        assert len(_requests_for(link.id, session)) == 2

    def test_renew_input_port__404_when_no_existing_link(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).renew_input_port(
                dp.id, port.id, actor=actor
            )
        assert exc.value.status_code == 404

    def test_renew_input_port__access_mode(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
        )
        access_mode = AccessModeFactory(name="a mode")
        TechnicalAssetOutputPortAssociationFactory(
            data_output=TechnicalAssetFactory(access_modes=[access_mode]),
            output_port=port,
        )
        link = InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.APPROVED,
            request__access_duration_type=AccessDurationType.TIME_BOUND,
            request__requested_duration_days=30,
            request__valid_until=date.today() + timedelta(days=10),
            request__access_mode_id=access_mode.id,
        )

        ip = AbstractDataProductService(session).renew_input_port(
            dp.id, port.id, actor=actor
        )

        assert ip.id == link.id
        reqs = _requests_for(link.id, session)
        assert len(reqs) == 2
        for req in reqs:
            assert req.access_mode_id == access_mode.id

    def test_revoke_input_port__revokes_the_active_grant(self, session):
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
        grant = _request_for(link, session)

        ip = AbstractDataProductService(session).revoke_input_port(
            dp.id, port.id, actor=actor
        )

        assert ip.id == link.id
        session.refresh(link)
        session.refresh(grant)
        assert link.status == InputPortStatus.REVOKED
        assert grant.revoked_at is not None
        assert grant.revoked_by_id == actor.id
        assert grant.decision == InputPortRequestDecision.APPROVED

    def test_revoke_input_port__raises_when_no_active_grant(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.PENDING,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).revoke_input_port(
                dp.id, port.id, actor=actor
            )
        assert exc.value.status_code == 400

    def test_revoke_input_port__404_when_no_existing_link(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).revoke_input_port(
                dp.id, port.id, actor=actor
            )
        assert exc.value.status_code == 404

    def test_cancel_input_port__cancels_the_pending_request(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        link = InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.PENDING,
        )
        pending = _request_for(link, session)

        ip = AbstractDataProductService(session).cancel_input_port_request(
            dp.id, port.id, actor=actor
        )

        assert ip.id == link.id
        session.refresh(link)
        session.refresh(pending)
        assert link.status == InputPortStatus.CANCELLED
        assert pending.decision == InputPortRequestDecision.CANCELLED
        assert pending.decided_by_id == actor.id
        assert pending.decided_on is not None
        assert pending.revoked_at is None

    def test_cancel_input_port__allows_a_new_request_afterwards(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        link = InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.PENDING,
        )

        AbstractDataProductService(session).cancel_input_port_request(
            dp.id, port.id, actor=actor
        )

        # A cancelled request frees up the "one pending request per link" slot
        AbstractDataProductService(session).renew_input_port(
            dp.id, port.id, actor=actor
        )

        reqs = _requests_for(link.id, session)
        assert len(reqs) == 2
        assert sum(r.decision == InputPortRequestDecision.PENDING for r in reqs) == 1
        assert sum(r.decision == InputPortRequestDecision.CANCELLED for r in reqs) == 1

    def test_cancel_input_port__raises_when_no_pending_request(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        InputPortFactory(
            consuming_abstract_data_product=dp,
            output_port=port,
            status=DecisionStatus.APPROVED,
        )

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).cancel_input_port_request(
                dp.id, port.id, actor=actor
            )
        assert exc.value.status_code == 400

    def test_cancel_input_port__404_when_no_existing_link(self, session):
        actor = UserFactory()
        dp = DataProductFactory()
        port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)

        with pytest.raises(HTTPException) as exc:
            AbstractDataProductService(session).cancel_input_port_request(
                dp.id, port.id, actor=actor
            )
        assert exc.value.status_code == 404
