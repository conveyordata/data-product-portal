from uuid import UUID

from app.abstract_data_product.type import AbstractDataProductType
from app.configuration.domains.schema import Domain
from app.data_products.output_ports.input_ports.schema import InputPortBase
from app.data_products.output_ports.schema import OutputPort
from app.data_products.status import AbstractDataProductStatus
from app.shared.schema import ORMModel


class AbstractDataProductInfo(ORMModel):
    name: str
    namespace: str
    abstract_data_product_type: AbstractDataProductType


class GetAbstractDataProductResponse(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    domain: Domain
    abstract_data_product_type: AbstractDataProductType
    status: AbstractDataProductStatus
    finalizers: list[str]


class InputPort(InputPortBase):
    output_port_id: UUID
    output_port: OutputPort
