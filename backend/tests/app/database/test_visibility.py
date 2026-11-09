from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import InputPort
from app.abstract_data_product.model import AbstractDataProduct
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.authorization.service import AuthorizationService
from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization
from app.data_products.model import DataProduct, DataProductVisibility
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.data_products.output_ports.model import OutputPort
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.database import SKIP_DATA_PRODUCT_VISIBILITY_FILTER
from app.database.visibility import (
    member_of,
    output_port_visible_ignoring_consumption,
    visible_ids,
)
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetRoleAssignmentFactory,
    ExplorationFactory,
    GroupFactory,
    GroupMembershipFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    TechnicalAssetFactory,
    UserFactory,
)
from tests.session_util import as_user

"""
Objects created through factories stay in the session's identity map, which bypasses the
visibility filter. Tests expunge or expire them so the lookup is a fresh, filtered query.
"""


def _direct_owner_identity(user):
    return user.id


def _group_owner_identity(user):
    group = GroupFactory()
    GroupMembershipFactory(group=group, member=user)
    return group.id


def test_acting_as__hidden_data_product_visible_for_currently_activated_admin(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    admin = UserFactory(admin_expiry=datetime(2099, 1, 1))

    with as_user(session, admin.id):
        loaded = session.get(DataProduct, data_product.id)

    assert loaded.id == data_product.id


def test_acting_as__hidden_data_product_not_visible_for_inactive_admin(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    admin = UserFactory(admin_expiry=None)

    with as_user(session, admin.id):
        loaded = session.get(DataProduct, data_product.id)

    assert loaded is None


def test_acting_as__hidden_data_product_not_visible_for_expired_admin(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    admin = UserFactory(admin_expiry=datetime(2000, 1, 1))

    with as_user(session, admin.id):
        loaded = session.get(DataProduct, data_product.id)

    assert loaded is None


def test_acting_as__hidden_data_product_visible_for_approved_user_assignment(session):
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
        loaded = session.get(DataProduct, data_product.id)

    assert loaded.id == data_product.id


def test_acting_as__hidden_data_product_not_visible_without_approved_user_assignment(
    session,
):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    user = UserFactory()

    with as_user(session, user.id):
        loaded = session.get(DataProduct, data_product.id)

    assert loaded is None


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_acting_as__hidden_data_product_not_visible_for_owner_of_approved_consumer(
    session, owner_identity
):
    producer = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    consumer = DataProductFactory()
    output_port = OutputPortFactory(
        data_product=producer, access_function=OutputPortAccessFunction.PRIVATE
    )
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
    producer_id, user_id = producer.id, user.id
    session.expunge_all()

    with as_user(session, user_id):
        loaded = session.get(DataProduct, producer_id)

    assert loaded is None


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_acting_as__hidden_data_product_id_not_visible_as_abstract_data_product_for_owner_of_approved_consumer(
    session, owner_identity
):
    producer = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    consumer = DataProductFactory()
    output_port = OutputPortFactory(
        data_product=producer, access_function=OutputPortAccessFunction.PRIVATE
    )
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

    assert visible_id is None


def test_acting_as__hidden_data_product_visible_for_system_account(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    system_user = UserFactory(external_id=SYSTEM_ACCOUNT_BOT_EXTERNAL_ID)

    with as_user(session, system_user.id):
        loaded = session.get(DataProduct, data_product.id)

    assert loaded.id == data_product.id


def test_acting_as__hidden_data_product_query_can_skip_visibility_filter(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)

    loaded = session.get(
        DataProduct,
        data_product.id,
        execution_options={SKIP_DATA_PRODUCT_VISIBILITY_FILTER: True},
    )

    assert loaded.id == data_product.id


def test_acting_as__hidden_data_product_query_without_current_user_is_not_filtered(
    session,
):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)

    loaded = session.get(DataProduct, data_product.id)

    assert loaded.id == data_product.id


def test_acting_as__hidden_data_product_column_query_without_current_user_is_not_filtered(
    session,
):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)

    visible_id = session.scalar(
        select(DataProduct.id).where(DataProduct.id == data_product.id)
    )

    assert visible_id == data_product.id


def test_acting_as__hidden_data_product_column_query_visible_for_admin_user(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    admin = UserFactory(admin_expiry=datetime(2099, 1, 1))

    with as_user(session, admin.id):
        visible_id = session.scalar(
            select(DataProduct.id).where(DataProduct.id == data_product.id)
        )

    assert visible_id == data_product.id


def test_acting_as__hidden_data_product_not_loaded_through_relationship(session):
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


def test_acting_as__discoverable_data_product_loaded_through_relationship(session):
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


def test_acting_as__invite_only_output_port_visible_for_currently_activated_admin(
    session,
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
    admin = UserFactory(admin_expiry=datetime(2099, 1, 1))
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, admin.id):
        loaded = session.get(OutputPort, output_port_id)

    assert loaded.id == output_port_id


def test_acting_as__invite_only_output_port_visible_for_approved_user_assignment(
    session,
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
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
        loaded = session.get(OutputPort, output_port_id)

    assert loaded.id == output_port_id


def test_acting_as__invite_only_output_port_visible_for_approved_data_product_assignment(
    session,
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
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
        loaded = session.get(OutputPort, output_port_id)

    assert loaded.id == output_port_id


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_acting_as__invite_only_output_port_visible_for_owner_of_approved_consumer(
    session, owner_identity
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
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
        loaded = session.get(OutputPort, output_port_id)

    assert loaded.id == output_port_id


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_acting_as__invite_only_sibling_output_port_not_visible_for_owner_of_consumer(
    session, owner_identity
):
    consumed_output_port = OutputPortFactory(
        access_function=OutputPortAccessFunction.PRIVATE
    )
    sibling_output_port = OutputPortFactory(
        data_product=consumed_output_port.data_product,
        access_function=OutputPortAccessFunction.PRIVATE,
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
        loaded = session.get(OutputPort, sibling_output_port_id)

    assert loaded is None


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_acting_as__invite_only_output_port_not_visible_for_owner_of_revoked_consumer(
    session, owner_identity
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
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
        loaded = session.get(OutputPort, output_port_id)

    assert loaded is None


@pytest.mark.parametrize(
    "owner_identity", [_direct_owner_identity, _group_owner_identity]
)
def test_acting_as__invite_only_output_port_not_visible_for_pending_consumer_role(
    session, owner_identity
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
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
        loaded = session.get(OutputPort, output_port_id)

    assert loaded is None


def test_acting_as__invite_only_output_port_not_visible_without_approved_user_assignment(
    session,
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)
    user = UserFactory()

    with as_user(session, user.id):
        loaded = session.get(OutputPort, output_port_id)

    assert loaded is None


def test_acting_as__invite_only_output_port_not_visible_without_approved_data_product_assignment(
    session,
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)
    user = UserFactory()

    with as_user(session, user.id):
        loaded = session.get(OutputPort, output_port_id)

    assert loaded is None


def test_acting_as__not_invite_only_output_port_visible_without_assignment(session):
    user = UserFactory()
    unrestricted = OutputPortFactory(
        access_function=OutputPortAccessFunction.UNRESTRICTED
    )
    restricted = OutputPortFactory(access_function=OutputPortAccessFunction.RESTRICTED)
    unrestricted_id = unrestricted.id
    restricted_id = restricted.id
    session.expunge(unrestricted)
    session.expunge(restricted)

    with as_user(session, user.id):
        unrestricted_visible = session.get(OutputPort, unrestricted_id)
        restricted_visible = session.get(OutputPort, restricted_id)

    assert unrestricted_visible.id == unrestricted_id
    assert restricted_visible.id == restricted_id


def test_acting_as__invite_only_output_port_visible_for_system_account(session):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
    system_user = UserFactory(external_id=SYSTEM_ACCOUNT_BOT_EXTERNAL_ID)
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, system_user.id):
        loaded = session.get(OutputPort, output_port_id)

    assert loaded.id == output_port_id


def test_acting_as__invite_only_output_port_query_can_skip_access_function_filter(
    session,
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)

    loaded = session.get(
        OutputPort,
        output_port_id,
        execution_options={"skip_output_port_access_function_filter": True},
    )

    assert loaded.id == output_port_id


def test_acting_as__invite_only_output_port_query_without_current_user_is_not_filtered(
    session,
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)

    loaded = session.get(OutputPort, output_port_id)

    assert loaded.id == output_port_id


def test_acting_as__invite_only_output_port_column_query_without_current_user_is_not_filtered(
    session,
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
    output_port_id = output_port.id
    session.expunge(output_port)

    assert (
        session.scalar(select(OutputPort.id).where(OutputPort.id == output_port_id))
        == output_port_id
    )


def test_acting_as__invite_only_output_port_column_query_visible_for_admin_user(
    session,
):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
    admin = UserFactory(admin_expiry=datetime(2099, 1, 1))
    output_port_id = output_port.id
    session.expunge(output_port)

    with as_user(session, admin.id):
        visible_id = session.scalar(
            select(OutputPort.id).where(OutputPort.id == output_port_id)
        )

    assert visible_id == output_port_id


def test_acting_as__technical_asset_of_hidden_data_product_not_visible_without_assignment(
    session,
):
    asset = _hidden_technical_asset()
    user = UserFactory()

    with as_user(session, user.id):
        loaded = _load(session, asset)

    assert loaded is None


@pytest.mark.parametrize("via_group", [False, True])
def test_acting_as__technical_asset_of_hidden_data_product_visible_for_member(
    session, via_group
):
    asset = _hidden_technical_asset()
    user = UserFactory()
    identity_id = user.id
    if via_group:
        group = GroupFactory()
        GroupMembershipFactory(group=group, member=user)
        identity_id = group.id
    DataProductRoleAssignmentFactory(
        data_product_id=asset.owner_id,
        identity_id=identity_id,
        role_id=RoleFactory.data_product_owner().id,
    )

    with as_user(session, user.id):
        loaded = _load(session, asset)

    assert loaded.id == asset.id


@pytest.mark.parametrize(
    "user_kwargs",
    [
        {"admin_expiry": datetime(2099, 1, 1)},
        {"external_id": SYSTEM_ACCOUNT_BOT_EXTERNAL_ID},
    ],
)
def test_acting_as__technical_asset_of_hidden_data_product_visible_for_admin_and_system_account(
    session, user_kwargs
):
    asset = _hidden_technical_asset()
    user = UserFactory(**user_kwargs)

    with as_user(session, user.id):
        loaded = _load(session, asset)

    assert loaded.id == asset.id


def test_acting_as__technical_asset_of_hidden_data_product_query_can_skip_visibility_filter(
    session,
):
    asset = _hidden_technical_asset()
    user = UserFactory()

    with as_user(session, user.id):
        loaded = _load(
            session,
            asset,
            execution_options={SKIP_DATA_PRODUCT_VISIBILITY_FILTER: True},
        )

    assert loaded.id == asset.id


def test_acting_as__technical_asset_of_discoverable_data_product_visible_without_assignment(
    session,
):
    asset = TechnicalAssetFactory()
    user = UserFactory()

    with as_user(session, user.id):
        loaded = _load(session, asset)

    assert loaded.id == asset.id


def _hidden_technical_asset() -> TechnicalAsset:
    return TechnicalAssetFactory(
        owner=DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    )


def _load(session, asset: TechnicalAsset, **kwargs) -> TechnicalAsset | None:
    return session.scalar(
        select(TechnicalAsset).where(TechnicalAsset.id == asset.id), **kwargs
    )


def _invite_only_output_port_consumed_by_member_of(user):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
    consumer = DataProductFactory()
    DataProductRoleAssignmentFactory(
        data_product_id=consumer.id,
        identity_id=user.id,
        role_id=RoleFactory.data_product_owner().id,
    )
    InputPortFactory(
        output_port=output_port,
        consuming_abstract_data_product=consumer,
        status=InputPortStatus.APPROVED,
    )
    return output_port


def test_output_port_visible_ignoring_consumption__hides_output_port_seen_only_as_consumer(
    session,
):
    user = UserFactory()
    output_port = _invite_only_output_port_consumed_by_member_of(user)
    stmt = select(OutputPort.id).where(OutputPort.id == output_port.id)

    with as_user(session, user.id):
        assert session.scalar(stmt) == output_port.id
        assert (
            session.scalar(
                stmt.where(
                    output_port_visible_ignoring_consumption(session, OutputPort)
                )
            )
            is None
        )


def test_output_port_visible_ignoring_consumption__keeps_member_of_owning_data_product(
    session,
):
    user = UserFactory()
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
    DataProductRoleAssignmentFactory(
        data_product_id=output_port.data_product_id,
        identity_id=user.id,
        role_id=RoleFactory.data_product_owner().id,
    )

    with as_user(session, user.id):
        assert (
            session.scalar(
                select(OutputPort.id).where(
                    OutputPort.id == output_port.id,
                    output_port_visible_ignoring_consumption(session, OutputPort),
                )
            )
            == output_port.id
        )


@pytest.mark.parametrize(
    ("decision", "owner_identity", "expected"),
    [
        (DecisionStatus.APPROVED, _direct_owner_identity, True),
        (DecisionStatus.APPROVED, _group_owner_identity, True),
        (DecisionStatus.PENDING, _direct_owner_identity, False),
        (DecisionStatus.DENIED, _direct_owner_identity, False),
    ],
)
def test_member_of__counts_approved_roles_directly_or_through_groups(
    session, decision, owner_identity, expected
):
    user = UserFactory()
    data_product = DataProductFactory()
    DataProductRoleAssignmentFactory(
        data_product_id=data_product.id,
        identity_id=owner_identity(user),
        role_id=RoleFactory.data_product_owner().id,
        decision=decision,
    )

    with as_user(session, user.id):
        assert session.scalar(select(member_of(session, data_product.id))) is expected


def test_member_of__nobody_is_a_member_without_a_user(session):
    data_product = DataProductFactory()

    assert session.scalar(select(member_of(session, data_product.id))) is False


def test_visible_ids__keeps_only_what_the_user_may_see(session):
    user = UserFactory()
    hidden = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    discoverable = DataProductFactory(visibility=DataProductVisibility.DISCOVERABLE)
    exploration = ExplorationFactory()
    unknown = uuid4()

    with as_user(session, user.id):
        seen = visible_ids(
            session, [hidden.id, discoverable.id, exploration.id, unknown]
        )

    assert seen == {discoverable.id, exploration.id}


def test_visible_ids__everything_is_visible_without_a_user(session):
    hidden = DataProductFactory(visibility=DataProductVisibility.HIDDEN)

    assert visible_ids(session, [hidden.id]) == {hidden.id}


def _stranger(data_product):
    return UserFactory()


def _member_with(decision, via_group=False, owner=True):
    def make(data_product):
        user = UserFactory()
        role = (
            RoleFactory.data_product_owner()
            if owner
            else RoleFactory(
                scope=Scope.DATA_PRODUCT,
                permissions=[AuthorizationAction.DATA_PRODUCT__CREATE_USER],
            )
        )
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            identity_id=_group_owner_identity(user) if via_group else user.id,
            role_id=role.id,
            decision=decision,
        )
        return user

    return make


def _member_of_consumer(data_product):
    user = UserFactory()
    consumer = DataProductFactory()
    DataProductRoleAssignmentFactory(
        data_product_id=consumer.id,
        identity_id=user.id,
        role_id=RoleFactory.data_product_owner().id,
    )
    InputPortFactory(
        output_port=OutputPortFactory(
            data_product=data_product,
            access_function=OutputPortAccessFunction.PRIVATE,
        ),
        consuming_abstract_data_product=consumer,
        status=InputPortStatus.APPROVED,
    )
    return user


def _system_account(data_product):
    return UserFactory(external_id=SYSTEM_ACCOUNT_BOT_EXTERNAL_ID)


def _admin(data_product):
    user = UserFactory(admin_expiry=datetime(2099, 1, 1))
    Authorization().assign_admin_role(user_id=str(user.id))
    return user


def _revoked_admin(data_product):
    return UserFactory(admin_expiry=datetime(2099, 1, 1))


_USERS = {
    "stranger": _stranger,
    "owner": _member_with(DecisionStatus.APPROVED),
    "other_role": _member_with(DecisionStatus.APPROVED, owner=False),
    "group_member": _member_with(DecisionStatus.APPROVED, via_group=True),
    "pending": _member_with(DecisionStatus.PENDING),
    "denied": _member_with(DecisionStatus.DENIED),
    "member_of_consumer": _member_of_consumer,
    "system_account": _system_account,
    "admin": _admin,
    "revoked_admin": _revoked_admin,
}


_KNOWN_DRIFT = {
    _revoked_admin: "revoke_admin removes the Casbin admin role but keeps admin_expiry",
    _admin: "reload_enforcer drops admin roles; nothing restores them from admin_expiry",
    _system_account: "Casbin has no grant for the system account; SQL lets it see all",
}


@pytest.mark.parametrize("visibility", list(DataProductVisibility))
@pytest.mark.parametrize("make_user", _USERS.values(), ids=_USERS.keys())
def test_visible_ids__agrees_with_casbin_route_check(
    session, request, visibility, make_user
):
    if visibility is DataProductVisibility.HIDDEN and make_user in _KNOWN_DRIFT:
        request.applymarker(
            pytest.mark.xfail(strict=True, reason=_KNOWN_DRIFT[make_user])
        )
    data_product = DataProductFactory(visibility=visibility)
    user = make_user(data_product)
    AuthorizationService(session).reload_enforcer()

    with as_user(session, user.id):
        sees = data_product.id in visible_ids(session, [data_product.id])
    may_read = Authorization().has_access(
        sub=str(user.id),
        dom=str(data_product.domain_id),
        obj=str(data_product.id),
        act=AuthorizationAction.HIDDEN__DATA_PRODUCT__READ,
    )

    assert sees is may_read
