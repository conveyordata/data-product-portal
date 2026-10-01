from datetime import datetime

import pytest
from sqlalchemy import select

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import InputPort
from app.abstract_data_product.model import AbstractDataProduct
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProduct, DataProductVisibility
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    GroupFactory,
    GroupMembershipFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)
from tests.session_util import as_user


def _direct_owner_identity(user):
    return user.id


def _group_owner_identity(user):
    group = GroupFactory()
    GroupMembershipFactory(group=group, member=user)
    return group.id


def test_hidden_data_product_visible_for_currently_activated_admin(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    admin = UserFactory(admin_expiry=datetime(2099, 1, 1))

    with as_user(session, admin.id):
        visible = session.get(DataProduct, data_product.id)

    assert visible.id == data_product.id


def test_hidden_data_product_not_visible_for_inactive_admin(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    admin = UserFactory(admin_expiry=None)

    with as_user(session, admin.id):
        visible = session.get(DataProduct, data_product.id)

    assert visible is None


def test_hidden_data_product_not_visible_for_expired_admin(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    admin = UserFactory(admin_expiry=datetime(2000, 1, 1))

    with as_user(session, admin.id):
        visible = session.get(DataProduct, data_product.id)

    assert visible is None


def test_hidden_data_product_visible_for_approved_user_assignment(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)

    role = RoleFactory(
        scope=Scope.DATA_PRODUCT,
        permissions=[AuthorizationAction.DATA_PRODUCT__CREATE_USER],
    )
    DataProductRoleAssignmentFactory(
        data_product_id=data_product.id, identity_id=user.id, role_id=role.id
    )

    with as_user(session, user.id):
        visible = session.get(DataProduct, data_product.id)

    assert visible.id == data_product.id


def test_hidden_data_product_not_visible_without_approved_user_assignment(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    user = UserFactory()

    with as_user(session, user.id):
        visible = session.get(DataProduct, data_product.id)

    assert visible is None


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_hidden_data_product_visible_for_owner_of_approved_consumer(
    session, owner_identity
):
    producer = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    consumer = DataProductFactory()
    output_port = OutputPortFactory(data_product=producer)
    user = UserFactory()

    owner_role = RoleFactory.data_product_owner()
    DataProductRoleAssignmentFactory(
        data_product_id=consumer.id,
        identity_id=owner_identity(user),
        role_id=owner_role.id,
    )
    InputPortFactory(
        output_port=output_port,
        consuming_abstract_data_product=consumer,
        status=InputPortStatus.APPROVED,
    )

    with as_user(session, user.id):
        visible = session.get(DataProduct, producer.id)

    assert visible.id == producer.id


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_hidden_data_product_not_visible_for_owner_of_revoked_consumer(
    session, owner_identity
):
    producer = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    consumer = DataProductFactory()
    output_port = OutputPortFactory(data_product=producer)
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
    producer_id = producer.id
    session.expunge(producer)

    with as_user(session, user.id):
        visible = session.get(DataProduct, producer_id)

    assert visible is None


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_hidden_data_product_not_visible_for_pending_consumer_role(
    session, owner_identity
):
    producer = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    consumer = DataProductFactory()
    output_port = OutputPortFactory(data_product=producer)
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
    producer_id = producer.id
    session.expunge(producer)

    with as_user(session, user.id):
        visible = session.get(DataProduct, producer_id)

    assert visible is None


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_hidden_data_product_visible_as_abstract_data_product_for_owner_of_approved_consumer(
    session, owner_identity
):
    producer = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    consumer = DataProductFactory()
    output_port = OutputPortFactory(data_product=producer)
    user = UserFactory()

    owner_role = RoleFactory.data_product_owner()
    DataProductRoleAssignmentFactory(
        data_product_id=consumer.id,
        identity_id=owner_identity(user),
        role_id=owner_role.id,
    )
    InputPortFactory(
        output_port=output_port,
        consuming_abstract_data_product=consumer,
        status=InputPortStatus.APPROVED,
    )

    with as_user(session, user.id):
        visible = session.get(AbstractDataProduct, producer.id)

    assert visible.id == producer.id


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_hidden_data_product_id_visible_as_abstract_data_product_for_owner_of_approved_consumer(
    session, owner_identity
):
    producer = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    consumer = DataProductFactory()
    output_port = OutputPortFactory(data_product=producer)
    user = UserFactory()

    owner_role = RoleFactory.data_product_owner()
    DataProductRoleAssignmentFactory(
        data_product_id=consumer.id,
        identity_id=owner_identity(user),
        role_id=owner_role.id,
    )
    InputPortFactory(
        output_port=output_port,
        consuming_abstract_data_product=consumer,
        status=InputPortStatus.APPROVED,
    )

    with as_user(session, user.id):
        visible_id = session.scalar(
            select(AbstractDataProduct.id).where(AbstractDataProduct.id == producer.id)
        )

    assert visible_id == producer.id


def test_hidden_data_product_visible_for_system_account(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    system_user = UserFactory(external_id=SYSTEM_ACCOUNT_BOT_EXTERNAL_ID)

    with as_user(session, system_user.id):
        visible = session.get(DataProduct, data_product.id)

    assert visible.id == data_product.id


def test_hidden_data_product_query_can_skip_visibility_filter(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)

    visible = session.get(
        DataProduct,
        data_product.id,
        execution_options={"skip_data_product_visibility_filter": True},
    )

    assert visible.id == data_product.id


def test_hidden_data_product_query_without_current_user_is_not_filtered(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)

    visible = session.get(DataProduct, data_product.id)

    assert visible.id == data_product.id


def test_hidden_data_product_column_query_without_current_user_is_not_filtered(
    session,
):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)

    visible_id = session.scalar(
        select(DataProduct.id).where(DataProduct.id == data_product.id)
    )

    assert visible_id == data_product.id


def test_hidden_data_product_column_query_visible_for_admin_user(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    admin = UserFactory(admin_expiry=datetime(2099, 1, 1))

    with as_user(session, admin.id):
        visible_id = session.scalar(
            select(DataProduct.id).where(DataProduct.id == data_product.id)
        )

    assert visible_id == data_product.id


def test_hidden_data_product_not_loaded_through_relationship(session):
    output_port = OutputPortFactory()
    hidden = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    input_port = InputPortFactory(
        output_port=output_port, consuming_abstract_data_product=hidden
    )
    user = UserFactory()
    session.flush()
    session.expire_all()

    with as_user(session, user.id):
        loaded = (
            session.scalars(select(InputPort).where(InputPort.id == input_port.id))
            .unique()
            .one()
        )

        assert loaded.consuming_abstract_data_product is None


def test_discoverable_data_product_loaded_through_relationship(session):
    output_port = OutputPortFactory()
    discoverable = DataProductFactory(visibility=DataProductVisibility.DISCOVERABLE)
    input_port = InputPortFactory(
        output_port=output_port, consuming_abstract_data_product=discoverable
    )
    user = UserFactory()
    session.flush()
    session.expire_all()

    with as_user(session, user.id):
        loaded = (
            session.scalars(select(InputPort).where(InputPort.id == input_port.id))
            .unique()
            .one()
        )

        assert loaded.consuming_abstract_data_product.id == discoverable.id
