from datetime import datetime

import pytest
from sqlalchemy import select

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.core.authz.actions import AuthorizationAction
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import OutputPort
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetRoleAssignmentFactory,
    GroupFactory,
    GroupMembershipFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)
from tests.session_util import as_user

"""
To ensure the tests work properly we explicitly expunge the output port from the session after creation.
This is because the session will cache the object and bypass the access type filter when retrieving it.
By expunging it, we force a fresh query to the database, which will apply the access type filter and ensure
that visibility rules are correctly enforced and can be tested

This is not an issue in normal tests, since we first check if you have access through casbin anyway for single object
access. And for list calls the filter will be used.
"""


def test_private_output_port_visible_for_currently_activated_admin(session):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    admin = UserFactory(admin_expiry=datetime(2099, 1, 1))
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, admin.id):
        visible = session.get(OutputPort, output_port_id)

    assert visible.id == output_port_id


def test_private_output_port_visible_for_approved_user_assignment(session):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)

    role = RoleFactory(
        scope=Scope.DATASET,
        permissions=[AuthorizationAction.HIDDEN__OUTPUT_PORT__READ],
    )
    DatasetRoleAssignmentFactory(
        output_port=output_port, user_id=user.id, role_id=role.id
    )
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, user.id):
        visible = session.get(OutputPort, output_port_id)

    assert visible.id == output_port_id


def test_private_output_port_visible_for_approved_data_product_assignment(session):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)

    role = RoleFactory(
        scope=Scope.DATA_PRODUCT,
        permissions=[AuthorizationAction.DATA_PRODUCT__CREATE_USER],
    )
    DataProductRoleAssignmentFactory(
        data_product_id=output_port.data_product_id,
        identity_id=user.id,
        role_id=role.id,
    )
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, user.id):
        visible = session.get(OutputPort, output_port_id)

    assert visible.id == output_port_id


def _direct_owner_identity(user):
    return user.id


def _group_owner_identity(user):
    group = GroupFactory()
    GroupMembershipFactory(group=group, member=user)
    return group.id


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_private_output_port_visible_for_owner_of_approved_consumer(
    session, owner_identity
):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    consumer = DataProductFactory()
    user = UserFactory()
    role = RoleFactory.data_product_owner()
    DataProductRoleAssignmentFactory(
        data_product_id=consumer.id,
        identity_id=owner_identity(user),
        role_id=role.id,
    )
    InputPortFactory(
        output_port=output_port,
        consuming_abstract_data_product=consumer,
        status=InputPortStatus.APPROVED,
    )
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, user.id):
        visible = session.get(OutputPort, output_port_id)

    assert visible.id == output_port_id


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_private_sibling_output_port_not_visible_for_owner_of_consumer(
    session, owner_identity
):
    consumed_output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    sibling_output_port = OutputPortFactory(
        data_product=consumed_output_port.data_product,
        access_type=OutputPortAccessType.PRIVATE,
    )
    consumer = DataProductFactory()
    user = UserFactory()
    role = RoleFactory.data_product_owner()
    DataProductRoleAssignmentFactory(
        data_product_id=consumer.id,
        identity_id=owner_identity(user),
        role_id=role.id,
    )
    InputPortFactory(
        output_port=consumed_output_port,
        consuming_abstract_data_product=consumer,
        status=InputPortStatus.APPROVED,
    )
    sibling_output_port_id = sibling_output_port.id
    session.expunge(sibling_output_port)

    with as_user(session, user.id):
        visible = session.get(OutputPort, sibling_output_port_id)

    assert visible is None


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_private_output_port_not_visible_for_owner_of_revoked_consumer(
    session, owner_identity
):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    consumer = DataProductFactory()
    user = UserFactory()
    role = RoleFactory.data_product_owner()
    DataProductRoleAssignmentFactory(
        data_product_id=consumer.id,
        identity_id=owner_identity(user),
        role_id=role.id,
    )
    InputPortFactory(
        output_port=output_port,
        consuming_abstract_data_product=consumer,
        status=InputPortStatus.REVOKED,
    )
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, user.id):
        visible = session.get(OutputPort, output_port_id)

    assert visible is None


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_private_output_port_not_visible_for_pending_consumer_role(
    session, owner_identity
):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    consumer = DataProductFactory()
    user = UserFactory()
    role = RoleFactory.data_product_owner()
    DataProductRoleAssignmentFactory(
        data_product_id=consumer.id,
        identity_id=owner_identity(user),
        role_id=role.id,
        decision=DecisionStatus.PENDING,
    )
    InputPortFactory(
        output_port=output_port,
        consuming_abstract_data_product=consumer,
        status=InputPortStatus.APPROVED,
    )
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, user.id):
        visible = session.get(OutputPort, output_port_id)

    assert visible is None


def test_private_output_port_not_visible_without_approved_user_assignment(session):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)
    user = UserFactory()

    with as_user(session, user.id):
        visible = session.get(OutputPort, output_port_id)

    assert visible is None


def test_private_output_port_not_visible_without_approved_data_product_assignment(
    session,
):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)
    user = UserFactory()

    with as_user(session, user.id):
        visible = session.get(OutputPort, output_port_id)

    assert visible is None


def test_non_private_output_port_visible_without_assignment(session):
    user = UserFactory()
    unrestricted = OutputPortFactory(access_type=OutputPortAccessType.UNRESTRICTED)
    restricted = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
    unrestricted_id = unrestricted.id
    restricted_id = restricted.id
    session.expunge(unrestricted)
    session.expunge(restricted)

    with as_user(session, user.id):
        unrestricted_visible = session.get(OutputPort, unrestricted_id)
        restricted_visible = session.get(OutputPort, restricted_id)

    assert unrestricted_visible.id == unrestricted_id
    assert restricted_visible.id == restricted_id


def test_private_output_port_visible_for_system_account(session):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    system_user = UserFactory(external_id=SYSTEM_ACCOUNT_BOT_EXTERNAL_ID)
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, system_user.id):
        visible = session.get(OutputPort, output_port_id)

    assert visible.id == output_port_id


def test_private_output_port_query_can_skip_access_type_filter(session):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)

    visible = session.get(
        OutputPort,
        output_port_id,
        execution_options={"skip_output_port_access_type_filter": True},
    )

    assert visible.id == output_port_id


def test_private_output_port_query_without_current_user_is_not_filtered(session):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)

    private = session.get(OutputPort, output_port_id)
    private.id = output_port_id


def test_private_output_port_column_query_without_current_user_is_not_filtered(session):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)

    assert (
        session.scalar(select(OutputPort.id).where(OutputPort.id == output_port_id))
        == output_port_id
    )


def test_private_output_port_column_query_visible_for_admin_user(session):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    admin = UserFactory(admin_expiry=datetime(2099, 1, 1))
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, admin.id):
        visible_id = session.scalar(
            select(OutputPort.id).where(OutputPort.id == output_port_id)
        )

    assert visible_id == output_port_id
