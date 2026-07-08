from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from pydantic import Field

from app.abstract_data_product.schema_response import AbstractDataProductInfo
from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_ports.input_ports.schema import InputPortBase
from app.data_products.output_ports.schema import OutputPort
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataProductOutputPortAssociationGet(ORMModel):
    id: UUID
    justification: str
    consuming_abstract_data_product_id: UUID
    output_port_id: UUID = Field(validation_alias="dataset_id")
    status: DecisionStatus
    requested_on: datetime

    requested_duration_days: Optional[int] = None
    expires_on: Optional[datetime] = None
    is_expiring_soon: bool = False
    renewed_on: Optional[datetime] = None
    total_range_start: Optional[datetime] = None
    total_range_end: Optional[datetime] = None

    # Nested schemas
    output_port: OutputPort = Field(validation_alias="dataset")
    consuming_abstract_data_product: AbstractDataProductInfo
    requested_by: User
    denied_by: Optional[User]
    approved_by: Optional[User]


class DataProductOutputPortAssociationsGet(BaseDataProductOutputPortAssociationGet):
    pass


class OutputPortInputPort(InputPortBase):
    consuming_abstract_data_product_id: UUID
    consuming_abstract_data_product: AbstractDataProductInfo


class GetInputPortsForOutputPortResponse(ORMModel):
    input_ports: Sequence[OutputPortInputPort]
