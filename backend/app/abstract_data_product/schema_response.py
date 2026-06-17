from uuid import UUID

from pydantic import Field

from app.abstract_data_product.type import AbstractDataProductType
from app.configuration.domains.schema import Domain
from app.data_products.output_ports.input_ports.schema import InputPortBase
from app.data_products.output_ports.schema import OutputPort
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


class InputPort(InputPortBase):
    output_port_id: UUID = Field(validation_alias="dataset_id")
    output_port: OutputPort = Field(validation_alias="dataset")
