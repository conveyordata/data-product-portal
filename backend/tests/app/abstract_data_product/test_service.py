from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from app.abstract_data_product.model import AbstractDataProduct
from app.abstract_data_product.service import AbstractDataProductService
from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.output_ports.enums import OutputPortAccessType
from app.settings import settings
from tests import test_session
from tests.factories import (
    AccessDurationFactory,
    DataProductFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    InputPortFactory,
    RoleFactory,
    UserFactory,
)


def _load_input_ports(adp: AbstractDataProduct) -> AbstractDataProduct:
    return test_session.get(
        AbstractDataProduct,
        adp.id,
        options=[selectinload(AbstractDataProduct.input_ports)],
        populate_existing=True,
    )


class TestAbstractDataProductService:
    @patch("app.abstract_data_product.service.email.send_dataset_link_email")
    def test_input_port_request_email_not_sent_when_requester_is_only_approver(
        self, mock_send_email
    ):
        actor = UserFactory()
        output_port = DatasetFactory(access_type=OutputPortAccessType.RESTRICTED)
        input_port = InputPortFactory(
            consuming_abstract_data_product=DataProductFactory(),
            dataset=output_port,
            requested_by=actor,
            status=DecisionStatus.PENDING,
        )
        approver_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(
            dataset=output_port,
            role_id=approver_role.id,
            user_id=actor.id,
        )
        background_tasks = MagicMock()

        AbstractDataProductService(
            test_session
        ).send_input_port_requested_emails_to_output_port_owners(
            [input_port],
            background_tasks,
            actor,
        )

        mock_send_email.assert_not_called()
        background_tasks.add_task.assert_not_called()

    @patch("app.abstract_data_product.service.email.send_dataset_link_email")
    def test_input_port_request_email_excludes_requester_from_approvers(
        self, mock_send_email
    ):
        actor = UserFactory()
        other_approver = UserFactory()
        output_port = DatasetFactory(access_type=OutputPortAccessType.RESTRICTED)
        input_port = InputPortFactory(
            consuming_abstract_data_product=DataProductFactory(),
            dataset=output_port,
            requested_by=actor,
            status=DecisionStatus.PENDING,
        )
        approver_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        for user in [actor, other_approver]:
            DatasetRoleAssignmentFactory(
                dataset=output_port,
                role_id=approver_role.id,
                user_id=user.id,
            )
        background_tasks = MagicMock()

        AbstractDataProductService(
            test_session
        ).send_input_port_requested_emails_to_output_port_owners(
            [input_port],
            background_tasks,
            actor,
        )

        mock_send_email.assert_called_once()
        approvers = mock_send_email.call_args.kwargs["approvers"]
        assert {approver.id for approver in approvers} == {other_approver.id}
        assert actor.id not in {approver.id for approver in approvers}
        background_tasks.add_task.assert_called_once_with(mock_send_email.return_value)

    def test_new_permanent_unrestricted_link_is_approved_without_time_bound_fields(
        self,
    ):
        actor = UserFactory()
        adp = _load_input_ports(DataProductFactory())
        output_port = DatasetFactory(access_type=OutputPortAccessType.UNRESTRICTED)

        input_port = AbstractDataProductService(test_session)._add_single_input_port(
            adp, output_port.id, "justification", actor=actor
        )
        test_session.flush()

        assert input_port.status == DecisionStatus.APPROVED
        assert input_port.dataset_id == output_port.id
        assert input_port.consuming_abstract_data_product_id == adp.id
        assert input_port.requested_by_id == actor.id
        assert input_port.requested_duration_days is None
        assert input_port.expires_on is None
        assert input_port.total_range_start is None
        assert input_port.total_range_end is None
        assert input_port.is_renewing is False
        assert input_port in adp.input_ports

    def test_new_permanent_restricted_link_is_pending(self):
        actor = UserFactory()
        adp = _load_input_ports(DataProductFactory())
        output_port = DatasetFactory(access_type=OutputPortAccessType.RESTRICTED)

        input_port = AbstractDataProductService(test_session)._add_single_input_port(
            adp, output_port.id, "justification", actor=actor
        )

        assert input_port.status == DecisionStatus.PENDING
        assert input_port.expires_on is None
        assert input_port.requested_duration_days is None

    def test_new_time_bound_unrestricted_link_sets_expiry_fields(self):
        actor = UserFactory()
        adp = _load_input_ports(DataProductFactory())
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
        )
        output_port = DatasetFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )

        before = datetime.now(timezone.utc)
        input_port = AbstractDataProductService(test_session)._add_single_input_port(
            adp, output_port.id, "justification", actor=actor
        )
        after = datetime.now(timezone.utc)
        test_session.flush()

        assert input_port.status == DecisionStatus.APPROVED
        assert input_port.requested_duration_days == 30
        assert (
            before + timedelta(days=30)
            <= input_port.expires_on
            <= after + timedelta(days=30)
        )
        assert before <= input_port.total_range_start <= after
        assert input_port.total_range_end == input_port.expires_on
        assert input_port.renewed_by_id is None
        assert input_port.renewed_on is None
        assert input_port.is_renewing is False

    def test_new_time_bound_restricted_link_only_sets_requested_duration_days(self):
        actor = UserFactory()
        adp = _load_input_ports(DataProductFactory())
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
        )
        output_port = DatasetFactory(
            access_type=OutputPortAccessType.RESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )

        input_port = AbstractDataProductService(test_session)._add_single_input_port(
            adp, output_port.id, "justification", actor=actor
        )

        assert input_port.status == DecisionStatus.PENDING
        assert input_port.requested_duration_days == 30
        assert input_port.expires_on is None
        assert input_port.total_range_start is None
        assert input_port.total_range_end is None

    def test_time_bound_without_access_duration_setting_raises_500(self):
        actor = UserFactory()
        adp = _load_input_ports(DataProductFactory())
        output_port = DatasetFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        with pytest.raises(HTTPException) as exc_info:
            AbstractDataProductService(test_session)._add_single_input_port(
                adp, output_port.id, "justification", actor=actor
            )

        assert exc_info.value.status_code == 500

    def test_duplicate_active_link_raises_400(self):
        actor = UserFactory()
        adp = DataProductFactory()
        output_port = DatasetFactory(access_type=OutputPortAccessType.UNRESTRICTED)
        InputPortFactory(
            consuming_abstract_data_product=adp,
            dataset=output_port,
            requested_by=actor,
            status=DecisionStatus.APPROVED,
        )
        adp = _load_input_ports(adp)

        with pytest.raises(HTTPException) as exc_info:
            AbstractDataProductService(test_session)._add_single_input_port(
                adp, output_port.id, "justification", actor=actor
            )

        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    def test_denied_link_does_not_block_new_request(self):
        actor = UserFactory()
        adp = DataProductFactory()
        output_port = DatasetFactory(access_type=OutputPortAccessType.UNRESTRICTED)
        denied_link = InputPortFactory(
            consuming_abstract_data_product=adp,
            dataset=output_port,
            requested_by=actor,
            status=DecisionStatus.DENIED,
        )
        adp = _load_input_ports(adp)

        input_port = AbstractDataProductService(test_session)._add_single_input_port(
            adp, output_port.id, "justification", actor=actor
        )

        assert input_port.id != denied_link.id
        assert input_port.status == DecisionStatus.APPROVED

    def test_renewal_of_expired_link_reuses_row_and_sets_renewal_fields(self):
        original_requester = UserFactory()
        renewing_actor = UserFactory()
        adp = DataProductFactory()
        output_port = DatasetFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
        )
        original_start = datetime.now() - timedelta(days=90)
        yesterday = datetime.now() - timedelta(days=1)
        expired_link = InputPortFactory(
            consuming_abstract_data_product=adp,
            dataset=output_port,
            requested_by=original_requester,
            status=DecisionStatus.EXPIRED,
            requested_duration_days=15,
            expires_on=yesterday,
            total_range_start=original_start,
            total_range_end=yesterday,
        )
        adp = _load_input_ports(adp)

        before_renewal = datetime.now(timezone.utc)
        input_port = AbstractDataProductService(test_session)._add_single_input_port(
            adp, output_port.id, "renewal justification", actor=renewing_actor
        )
        after_renewal = datetime.now(timezone.utc)
        test_session.flush()

        assert input_port.id == expired_link.id
        assert (
            test_session.query(input_port.__class__)
            .filter_by(
                consuming_abstract_data_product_id=adp.id,
                dataset_id=output_port.id,
            )
            .count()
            == 1
        )
        # Unrestricted so auto approved
        assert input_port.status == DecisionStatus.APPROVED
        # Since it got auto approved the is_renewing should be put on False
        assert input_port.is_renewing is False
        assert (
            before_renewal + timedelta(days=30)
            <= input_port.expires_on
            <= after_renewal + timedelta(days=30)
        )
        assert input_port.total_range_end == input_port.expires_on
        assert input_port.renewed_by_id == renewing_actor.id
        assert before_renewal <= input_port.renewed_on <= after_renewal

        # Range doesn't get updated
        assert input_port.total_range_start == original_start
        assert input_port.requested_duration_days == 15
        assert input_port.requested_by_id == original_requester.id

    def test_renewal_of_expiring_soon_approved_link_extends_expiry_without_changing_status(
        self,
    ):
        actor = UserFactory()
        adp = DataProductFactory()
        output_port = DatasetFactory(
            access_type=OutputPortAccessType.UNRESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
        )
        expiring_soon_on = datetime.now() + timedelta(
            days=settings.ACCESS_DURATION_EXPIRING_SOON_DAYS - 1
        )
        active_link = InputPortFactory(
            consuming_abstract_data_product=adp,
            dataset=output_port,
            requested_by=actor,
            status=DecisionStatus.APPROVED,
            expires_on=expiring_soon_on,
            total_range_end=expiring_soon_on,
        )
        assert active_link.is_expiring_soon is True
        adp = _load_input_ports(adp)

        input_port = AbstractDataProductService(test_session)._add_single_input_port(
            adp, output_port.id, "renewal justification", actor=actor
        )
        test_session.flush()

        assert input_port.id == active_link.id
        # Status was already APPROVED (not EXPIRED), so the renewal branch
        # leaves it untouched even though the expiry fields are extended.
        assert input_port.status == DecisionStatus.APPROVED
        # Unrestricted so auto approved - the renewal is no longer in flight.
        assert input_port.is_renewing is False
        assert input_port.expires_on.replace(tzinfo=None) > expiring_soon_on
        assert input_port.total_range_end == input_port.expires_on
        assert input_port.renewed_by_id == actor.id
        assert input_port.renewed_on is not None

    def test_renewal_of_restricted_expired_link_moves_to_pending_without_new_expiry(
        self,
    ):
        actor = UserFactory()
        adp = DataProductFactory()
        output_port = DatasetFactory(
            access_type=OutputPortAccessType.RESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
        )
        old_expiry = datetime.now() - timedelta(days=1)
        expired_link = InputPortFactory(
            consuming_abstract_data_product=adp,
            dataset=output_port,
            requested_by=actor,
            status=DecisionStatus.EXPIRED,
            expires_on=old_expiry,
            renewed_by=None,
            renewed_on=None,
        )
        adp = _load_input_ports(adp)

        input_port = AbstractDataProductService(test_session)._add_single_input_port(
            adp, output_port.id, "renewal justification", actor=actor
        )

        assert input_port.id == expired_link.id
        # A restricted output port needs re-approval, so renewal only flips
        # the status back to pending - it does NOT stamp new expiry/renewal
        # fields until that pending request is approved.
        assert input_port.status == DecisionStatus.PENDING
        assert input_port.is_renewing is True
        assert input_port.expires_on == old_expiry
        assert input_port.renewed_by_id is None
        assert input_port.renewed_on is None
