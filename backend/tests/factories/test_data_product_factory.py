from app.authorization.service import DATA_PRODUCT_READER_ROLE
from app.core.authz.authorization import Authorization
from app.data_products.model import DataProductVisibility
from tests.factories import DataProductFactory


def test_syncs_public_reader_grouping_for_discoverable_data_products():
    data_product = DataProductFactory(visibility=DataProductVisibility.DISCOVERABLE)
    assert Authorization().has_resource_role(
        user_id="*",
        role_id=DATA_PRODUCT_READER_ROLE,
        resource_id=str(data_product.id),
    )


def test_does_not_assign_public_reader_grouping_for_hidden_data_products():
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    assert not Authorization().has_resource_role(
        user_id="*",
        role_id=DATA_PRODUCT_READER_ROLE,
        resource_id=str(data_product.id),
    )
