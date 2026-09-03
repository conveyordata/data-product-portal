from datetime import datetime

import pytest
from sqlalchemy import select

from app.abstract_data_product.model import AbstractDataProduct
from app.authorization.roles.schema import Scope
from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProduct, DataProductVisibility
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from tests.session_util import as_user


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
        data_product_id=data_product.id, user_id=user.id, role_id=role.id
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


def test_hidden_data_product_not_visible_when_queried_as_abstract_data_product(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    user = UserFactory()

    with as_user(session, user.id):
        visible = session.get(AbstractDataProduct, data_product.id)

    assert visible is None


def test_hidden_data_product_id_not_visible_when_queried_as_abstract_data_product(
    session,
):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    user = UserFactory()

    with as_user(session, user.id):
        visible_id = session.scalar(
            select(AbstractDataProduct.id).where(
                AbstractDataProduct.id == data_product.id
            )
        )

    assert visible_id is None


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


def test_hidden_data_product_query_requires_current_user_without_skip_flag(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)

    with pytest.raises(
        Exception,
        match="User id must be set when skip_data_product_visibility_filter is False or not set",
    ):
        session.get(DataProduct, data_product.id)


def test_hidden_data_product_column_query_requires_current_user_without_skip_flag(
    session,
):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)

    with pytest.raises(
        Exception,
        match="User id must be set when skip_data_product_visibility_filter is False or not set",
    ):
        session.scalar(select(DataProduct.id).where(DataProduct.id == data_product.id))


def test_hidden_data_product_column_query_visible_for_admin_user(session):
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    admin = UserFactory(admin_expiry=datetime(2099, 1, 1))

    with as_user(session, admin.id):
        visible_id = session.scalar(
            select(DataProduct.id).where(DataProduct.id == data_product.id)
        )

    assert visible_id == data_product.id
