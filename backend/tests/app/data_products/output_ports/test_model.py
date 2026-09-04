from datetime import datetime

import pytest
from sqlalchemy import select

from app.authorization.roles.schema import Scope
from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.core.authz.actions import AuthorizationAction
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import OutputPort
from app.settings import settings
from tests.factories import (
    DatasetRoleAssignmentFactory,
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


def test_private_output_port_not_visible_without_approved_user_assignment(session):
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


def test_private_output_port_query_requires_current_user_without_skip_flag(session):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)

    with pytest.raises(
        Exception,
        match="User id must be set when skip_output_port_access_type_filter is False or not set",
    ):
        session.get(OutputPort, output_port_id)


def test_private_output_port_column_query_requires_current_user_without_skip_flag(
    session,
):
    output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)

    with pytest.raises(
        Exception,
        match="User id must be set when skip_output_port_access_type_filter is False or not set",
    ):
        session.scalar(select(OutputPort.id).where(OutputPort.id == output_port_id))


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
