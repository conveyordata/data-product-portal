from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.core.authz import Authorization
from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProduct, DataProductVisibility
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.service import DataProductService
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)

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
            access_type=OutputPortAccessType.PRIVATE,
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

    def test_sync_consumer_reader_grouping__consumer_has_access(self, session):
        result = self.setup_data_product_with_consumer()
        DataProductService(session)._sync_consumer_reader_grouping(result.producer.id)
        assert Authorization().has_access(
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
            access_type=OutputPortAccessType.PRIVATE,
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
        DataProductService(session)._sync_consumer_reader_grouping(result.producer.id)
        assert Authorization().has_access(
            act=AuthorizationAction.HIDDEN__DATA_PRODUCT__READ,
            dom=str(result.producer.domain.id),
            obj=str(result.producer.id),
            sub=str(result.user.id),
        )

        result.input_port.status = InputPortStatus.REVOKED
        session.flush()
        DataProductService(session)._sync_consumer_reader_grouping(result.producer.id)
        assert not Authorization().has_access(
            act=AuthorizationAction.HIDDEN__DATA_PRODUCT__READ,
            dom=str(result.producer.domain.id),
            obj=str(result.producer.id),
            sub=str(result.user.id),
        )
