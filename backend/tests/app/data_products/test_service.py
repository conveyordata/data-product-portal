from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.authorization.role_assignments.enums import DecisionStatus
from app.core.authz import Authorization
from app.core.authz.actions import AuthorizationAction
from app.core.context import close_event_context, open_event_context, pop_events
from app.data_products.model import DataProduct, DataProductVisibility
from app.data_products.output_port_technical_assets_link.service import (
    TechnicalAssetOutputPortService,
)
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_request import DataProductAboutUpdate
from app.data_products.service import DataProductService
from app.data_products.technical_assets.service import TechnicalAssetService
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    TechnicalAssetFactory,
    TechnicalAssetOutputPortAssociationFactory,
    UserFactory,
)
from tests.session_util import as_user

if TYPE_CHECKING:
    from app.abstract_data_product.input_ports.model import InputPort
    from app.users.model import User


@dataclass
class HiddenDataProductSetupResult:
    producer: "DataProduct"
    consumer: "DataProduct"
    user: "User"
    input_port: "InputPort"


class TestDataProductService:
    @staticmethod
    def setup_data_product_with_consumer(
        visibility: DataProductVisibility = DataProductVisibility.HIDDEN,
    ) -> HiddenDataProductSetupResult:
        producer = DataProductFactory(visibility=visibility)
        consumer = DataProductFactory()
        output_port = OutputPortFactory(
            data_product=producer,
            access_function=OutputPortAccessFunction.PRIVATE,
        )
        user = UserFactory()

        owner_role = RoleFactory.data_product_owner()
        DataProductRoleAssignmentFactory(
            data_product_id=consumer.id,
            identity_id=user.id,
            role_id=owner_role.id,
        )
        input_port = InputPortFactory(
            output_port=output_port,
            consuming_abstract_data_product=consumer,
            status=InputPortStatus.APPROVED,
        )
        return HiddenDataProductSetupResult(
            producer=producer, consumer=consumer, user=user, input_port=input_port
        )

    def test_sync_consumer_reader_grouping__consumer_has_no_access_to_producer(
        self, session
    ):
        result = self.setup_data_product_with_consumer()
        DataProductService(session)._sync_consumer_reader_grouping(result.producer.id)
        assert not Authorization().has_access(
            act=AuthorizationAction.HIDDEN__DATA_PRODUCT__READ,
            dom=str(result.producer.domain.id),
            obj=str(result.producer.id),
            sub=str(result.user.id),
        )

    def test_sync_consumer_reader_grouping__consumer_has_access_to_consumed_output_port(
        self, session
    ):
        result = self.setup_data_product_with_consumer(
            visibility=DataProductVisibility.DISCOVERABLE
        )
        other_output_port = OutputPortFactory(
            data_product=result.producer,
            access_function=OutputPortAccessFunction.PRIVATE,
        )
        DataProductService(session)._sync_consumer_reader_grouping(result.producer.id)

        assert Authorization().has_access(
            act=AuthorizationAction.HIDDEN__OUTPUT_PORT__READ,
            dom=str(result.producer.domain.id),
            obj=str(result.input_port.output_port_id),
            parent=str(result.producer.id),
            sub=str(result.user.id),
        )
        assert not Authorization().has_access(
            act=AuthorizationAction.HIDDEN__OUTPUT_PORT__READ,
            dom=str(result.producer.domain.id),
            obj=str(other_output_port.id),
            parent=str(result.producer.id),
            sub=str(result.user.id),
        )

    def test_sync_consumer_reader_grouping__previous_consumer_access_will_be_removed(
        self, session
    ):
        result = self.setup_data_product_with_consumer()
        output_port_read = {
            "act": AuthorizationAction.HIDDEN__OUTPUT_PORT__READ,
            "dom": str(result.producer.domain.id),
            "obj": str(result.input_port.output_port_id),
            "parent": str(result.producer.id),
            "sub": str(result.user.id),
        }
        DataProductService(session)._sync_consumer_reader_grouping(result.producer.id)
        assert Authorization().has_access(**output_port_read)

        result.input_port.status = InputPortStatus.REVOKED
        session.flush()
        DataProductService(session)._sync_consumer_reader_grouping(result.producer.id)
        assert not Authorization().has_access(**output_port_read)

    def test_sync_consumer_reader_grouping__keeps_links_the_acting_user_cannot_see(
        self, session
    ):
        result = self.setup_data_product_with_consumer()
        other_output_port = OutputPortFactory(
            data_product=result.producer,
            access_function=OutputPortAccessFunction.PRIVATE,
        )
        other_consumer = DataProductFactory()
        InputPortFactory(
            output_port=other_output_port,
            consuming_abstract_data_product=other_consumer,
            status=InputPortStatus.APPROVED,
        )
        service = DataProductService(session)
        service._sync_consumer_reader_grouping(result.producer.id)

        with as_user(session, result.user.id):
            service._sync_consumer_reader_grouping(result.producer.id)

        links = {
            (str(link.consumer_id), str(link.producer_output_port_id))
            for link in Authorization().get_input_port_link(
                producer_data_product_id=result.producer.id
            )
        }
        assert (str(other_consumer.id), str(other_output_port.id)) in links

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
