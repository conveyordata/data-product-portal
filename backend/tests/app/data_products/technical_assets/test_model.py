from datetime import datetime

import pytest
from sqlalchemy import select

from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.data_products.model import DataProductVisibility
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.database import SKIP_DATA_PRODUCT_VISIBILITY_FILTER
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    GroupFactory,
    GroupMembershipFactory,
    RoleFactory,
    TechnicalAssetFactory,
    UserFactory,
)
from tests.session_util import as_user


def test_technical_asset_of_hidden_data_product_not_visible_without_assignment(
    session,
):
    asset = _hidden_technical_asset()
    user = UserFactory()

    with as_user(session, user.id):
        visible = _load(session, asset)

    assert visible is None


@pytest.mark.parametrize("via_group", [False, True])
def test_technical_asset_of_hidden_data_product_visible_for_member(session, via_group):
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
        visible = _load(session, asset)

    assert visible.id == asset.id


@pytest.mark.parametrize(
    "user_kwargs",
    [
        {"admin_expiry": datetime(2099, 1, 1)},
        {"external_id": SYSTEM_ACCOUNT_BOT_EXTERNAL_ID},
    ],
)
def test_technical_asset_of_hidden_data_product_visible_for_admin_and_system_account(
    session, user_kwargs
):
    asset = _hidden_technical_asset()
    user = UserFactory(**user_kwargs)

    with as_user(session, user.id):
        visible = _load(session, asset)

    assert visible.id == asset.id


def test_technical_asset_of_hidden_data_product_query_can_skip_visibility_filter(
    session,
):
    asset = _hidden_technical_asset()
    user = UserFactory()

    with as_user(session, user.id):
        visible = _load(
            session,
            asset,
            execution_options={SKIP_DATA_PRODUCT_VISIBILITY_FILTER: True},
        )

    assert visible.id == asset.id


def test_technical_asset_of_discoverable_data_product_visible_without_assignment(
    session,
):
    asset = TechnicalAssetFactory()
    user = UserFactory()

    with as_user(session, user.id):
        visible = _load(session, asset)

    assert visible.id == asset.id


def _hidden_technical_asset() -> TechnicalAsset:
    return TechnicalAssetFactory(
        owner=DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    )


def _load(session, asset: TechnicalAsset, **kwargs) -> TechnicalAsset | None:
    return session.scalar(
        select(TechnicalAsset).where(TechnicalAsset.id == asset.id), **kwargs
    )
