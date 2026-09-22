from unittest.mock import MagicMock, patch

from app.abstract_data_product.service import AbstractDataProductService
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.output_ports.enums import OutputPortAccessType
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetRoleAssignmentFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)
from tests.session_util import as_user


class TestAbstractDataProductService:
    @patch("app.abstract_data_product.service.email.send_dataset_link_email")
    def test_input_port_request_email_not_sent_when_requester_is_only_approver(
        self,
        mock_send_email,
        session,
    ):
        actor = UserFactory()
        output_port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        input_port = InputPortFactory(
            consuming_abstract_data_product=DataProductFactory(),
            output_port=output_port,
            request__requested_by=actor,
            status=DecisionStatus.PENDING,
        )
        approver_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(
            output_port=output_port,
            role_id=approver_role.id,
            user_id=actor.id,
        )
        background_tasks = MagicMock()

        with as_user(session, UserFactory().id):
            AbstractDataProductService(
                session
            ).send_input_port_requested_emails_to_output_port_owners(
                [input_port],
                background_tasks,
                actor,
            )

        mock_send_email.assert_not_called()
        background_tasks.add_task.assert_not_called()

    @patch("app.abstract_data_product.service.email.send_dataset_link_email")
    def test_input_port_request_email_excludes_requester_from_approvers(
        self,
        mock_send_email,
        session,
    ):
        actor = UserFactory()
        other_approver = UserFactory()
        output_port = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        input_port = InputPortFactory(
            consuming_abstract_data_product=DataProductFactory(),
            output_port=output_port,
            request__requested_by=actor,
            status=DecisionStatus.PENDING,
        )
        approver_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        for user in [actor, other_approver]:
            DatasetRoleAssignmentFactory(
                output_port=output_port,
                role_id=approver_role.id,
                user_id=user.id,
            )
        background_tasks = MagicMock()

        with as_user(session, UserFactory().id):
            AbstractDataProductService(
                session
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

    def test_get_input_ports__filters_private_for_not_owner(self, session):
        """A non-owner should not be able to see the input port, if we want to change functionality, we should at least redact it"""
        op = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        ip = InputPortFactory(output_port=op)

        with as_user(session, UserFactory().id):
            input_ports = AbstractDataProductService(session).get_input_ports(
                ip.consuming_abstract_data_product_id,
            )
        assert len(input_ports) == 0

    def test_get_input_ports__shows_private_for_owner(self, session):
        op = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        ip = InputPortFactory(output_port=op)
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)

        DataProductRoleAssignmentFactory(
            data_product_id=ip.consuming_abstract_data_product_id,
            identity_id=user.id,
            role_id=RoleFactory.data_product_owner().id,
        )

        with as_user(session, user.id):
            input_ports = AbstractDataProductService(session).get_input_ports(
                ip.consuming_abstract_data_product_id,
            )
        assert ip.id in [ip.id for ip in input_ports]
