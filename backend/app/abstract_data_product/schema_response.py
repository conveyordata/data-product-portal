from typing import Optional
from uuid import UUID

from pydantic import PrivateAttr, computed_field, field_serializer

from app.abstract_data_product.type import AbstractDataProductType
from app.configuration.domains.schema import Domain
from app.core.authz import REDACTION_VALUE
from app.data_products.output_ports.input_ports.schema import InputPortBase
from app.data_products.output_ports.schema import OutputPort
from app.data_products.status import AbstractDataProductStatus
from app.shared.schema import ORMModel


class AbstractDataProductInfo(ORMModel):
    name: str
    namespace: str
    abstract_data_product_type: AbstractDataProductType
    _is_redacted: Optional[bool] = PrivateAttr(default=None)

    def set_redacted(self, status: bool) -> None:
        self._is_redacted = status

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_redacted(self) -> bool:
        if self._is_redacted is None:
            raise ValueError("is_redacted must be set")
        return self._is_redacted

    @field_serializer("name", "namespace")
    def serialize_redacted_fields(self, value: str) -> str:
        if self.is_redacted:
            return REDACTION_VALUE
        return value


class GetAbstractDataProductResponse(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    domain: Domain
    abstract_data_product_type: AbstractDataProductType
    status: AbstractDataProductStatus
    finalizers: list[str]


class AbstractDataProductInputPort(InputPortBase):
    output_port_id: UUID
    output_port: OutputPort
