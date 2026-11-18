from sqlalchemy import select

from app.authorization.role_assignments.enums import DecisionStatus
from app.core.context import close_event_context, open_event_context, pop_events
from app.data_products.model import DataProduct
from app.data_products.output_port_technical_assets_link.service import (
    TechnicalAssetOutputPortService,
)
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_request import DataProductAboutUpdate
from app.data_products.service import DataProductService
from app.data_products.technical_assets.model import TechnicalAsset
from app.data_products.technical_assets.service import TechnicalAssetService
from app.technical_asset_configuration.base_model import TechnicalAssetConfiguration
from tests.factories import (
    DataProductFactory,
    OutputPortFactory,
    TechnicalAssetFactory,
    TechnicalAssetOutputPortAssociationFactory,
    UserFactory,
)


class TestDataProductService:
    def test_remove_data_product__deletes_technical_assets_and_configurations(
        self, session
    ):
        data_product = DataProductFactory()
        technical_asset = TechnicalAssetFactory(owner=data_product)
        data_product_id = data_product.id
        technical_asset_id = technical_asset.id
        configuration_id = technical_asset.configuration_id
        configuration_type = type(technical_asset.configuration)

        DataProductService(session).remove_data_product(data_product_id)

        assert session.get(DataProduct, data_product_id) is None
        assert session.get(TechnicalAsset, technical_asset_id) is None
        assert session.get(configuration_type, configuration_id) is None
        assert session.get(TechnicalAssetConfiguration, configuration_id) is None

    def test_recalculate_search__sets_embeddings(self, session):
        data_product = DataProductFactory(name="Churn", description=None, about=None)
        TechnicalAssetFactory(owner=data_product)
        OutputPortFactory(data_product=data_product)

        DataProductService(session).recalculate_search(data_product.id)

        assert self._embeddings(session, data_product.id) is not None

    def test_recalculate_search__queues_no_events(self, session):
        data_product = DataProductFactory()
        token = open_event_context()
        try:
            DataProductService(session).recalculate_search(data_product.id)
            session.flush()
            assert pop_events() == []
        finally:
            close_event_context(token)

    def test_recalculate_search__keeps_events_of_pending_changes(self, session):
        data_product = DataProductFactory()
        token = open_event_context()
        try:
            data_product.name = "Renamed"
            DataProductService(session).recalculate_search(data_product.id)
            assert len(pop_events()) == 1
        finally:
            close_event_context(token)

    def test_recalculate_search_for_all_data_products(self, session):
        data_products = [DataProductFactory() for _ in range(51)]  # 2 batches
        DataProductService(session).recalculate_search_for_all_data_products()
        assert (
            None
            not in session.scalars(
                select(DataProduct.embeddings).where(
                    DataProduct.id.in_([dp.id for dp in data_products])
                )
            ).all()
        )

    def test_update_data_product_about__recalculates_search(self, session):
        data_product = DataProductFactory()
        before = self._embeddings(session, data_product.id)

        DataProductService(session).update_data_product_about(
            data_product.id, DataProductAboutUpdate(about="Weekly churn predictions")
        )

        assert self._embeddings(session, data_product.id) != before

    def test_remove_output_port__recalculates_data_product_search(self, session):
        data_product = DataProductFactory()
        output_port = OutputPortFactory(data_product=data_product)
        DataProductService(session).recalculate_search(data_product.id)
        before = self._embeddings(session, data_product.id)

        OutputPortService(session).remove_output_port(output_port.id, data_product.id)

        assert self._embeddings(session, data_product.id) != before

    def test_remove_technical_asset__recalculates_data_product_search(self, session):
        link = TechnicalAssetOutputPortAssociationFactory()
        data_product_id = link.output_port.data_product_id
        DataProductService(session).recalculate_search(data_product_id)
        before = self._embeddings(session, data_product_id)

        TechnicalAssetService(session).remove_technical_asset(
            data_product_id, link.technical_asset_id
        )

        assert self._embeddings(session, data_product_id) != before

    def test_approve_technical_asset_link__recalculates_data_product_search(
        self, session
    ):
        link = TechnicalAssetOutputPortAssociationFactory(status=DecisionStatus.PENDING)
        data_product_id = link.output_port.data_product_id
        DataProductService(session).recalculate_search(data_product_id)
        before = self._embeddings(session, data_product_id)

        TechnicalAssetOutputPortService(session).approve_technical_asset_link(
            data_product_id=data_product_id,
            technical_asset_id=link.technical_asset_id,
            output_port_id=link.output_port_id,
            actor=UserFactory(),
        )

        assert self._embeddings(session, data_product_id) != before

    def test_unlink_output_port_from_technical_asset__recalculates_data_product_search(
        self, session
    ):
        link = TechnicalAssetOutputPortAssociationFactory()
        data_product_id = link.output_port.data_product_id
        DataProductService(session).recalculate_search(data_product_id)
        before = self._embeddings(session, data_product_id)

        TechnicalAssetService(session).unlink_output_port_from_technical_asset(
            data_product_id, link.technical_asset_id, link.output_port_id
        )

        assert self._embeddings(session, data_product_id) != before

    @staticmethod
    def _embeddings(session, data_product_id) -> list[float] | None:
        embeddings = session.scalar(
            select(DataProduct.embeddings).where(DataProduct.id == data_product_id)
        )
        return None if embeddings is None else list(embeddings)
