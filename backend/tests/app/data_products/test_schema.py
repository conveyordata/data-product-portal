from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.model import DataProduct
from app.data_products.schema import DataProductEmbedModel
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.database import UNFILTERED
from tests.factories import (
    DataProductFactory,
    OutputPortFactory,
    TechnicalAssetFactory,
    TechnicalAssetOutputPortAssociationFactory,
)


class TestDataProductEmbedModel:
    def test_model_validate__only_keeps_technical_assets_exposed_via_output_port(
        self, session
    ):
        data_product = DataProductFactory()
        output_port = OutputPortFactory(data_product=data_product)
        for name, status in [
            ("approved", DecisionStatus.APPROVED),
            ("pending", DecisionStatus.PENDING),
            ("denied", DecisionStatus.DENIED),
        ]:
            TechnicalAssetOutputPortAssociationFactory(
                output_port=output_port,
                technical_asset=TechnicalAssetFactory(owner=data_product, name=name),
                status=status,
            )
        TechnicalAssetFactory(owner=data_product, name="unlinked")
        session.flush()
        session.expire_all()

        loaded = session.scalar(
            select(DataProduct)
            .where(DataProduct.id == data_product.id)
            .options(
                selectinload(DataProduct.datasets),
                selectinload(DataProduct.technical_assets).selectinload(
                    TechnicalAsset.output_port_links
                ),
            ),
            execution_options=UNFILTERED,
        )

        embed = DataProductEmbedModel.model_validate(loaded)

        assert [ta.name for ta in embed.technical_assets] == ["approved"]
