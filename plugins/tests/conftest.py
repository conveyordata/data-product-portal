from uuid import uuid4

import pytest

import app.main  # noqa: F401
from app.configuration.data_product_types.enums import DataProductIconKey
from app.configuration.data_product_types.schema import DataProductType
from app.configuration.domains.schema import Domain
from app.data_products.schema import DataProduct
from app.data_products.status import AbstractDataProductStatus
from app.data_products.technical_assets.enums import TechnicalMapping
from app.technical_asset_configuration.base_schema import (
    PluginContext,
    TechnicalAssetContext,
)


@pytest.fixture
def plugin_context() -> PluginContext:
    return PluginContext(
        technical_asset=TechnicalAssetContext(
            namespace="orders", technical_mapping=TechnicalMapping.Default
        ),
        data_product=DataProduct(
            id=uuid4(),
            name="Customer 360",
            namespace="customer360",
            description="",
            status=AbstractDataProductStatus.ACTIVE,
            type=DataProductType(
                id=uuid4(),
                name="some-type",
                description="",
                icon_key=DataProductIconKey.REPORTING,
            ),
        ),
        domain=Domain(id=uuid4(), name="finance", description=""),
    )
