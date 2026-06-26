from unittest.mock import MagicMock, patch

from app.abstract_data_product.service import AbstractDataProductService
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.output_ports.enums import OutputPortAccessType
from tests import test_session
from tests.factories import (
    DataProductFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    InputPortFactory,
    RoleFactory,
    UserFactory,
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
