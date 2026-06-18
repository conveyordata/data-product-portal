from typing import Annotated, Optional
from uuid import UUID
from warnings import deprecated

from annotated_types import MinLen
from pydantic import field_validator

from app.data_products.status import AbstractDataProductStatus
from app.shared.schema import ORMModel


class DataProductUpdate(ORMModel):
    name: str
    namespace: str
    description: str
    type_id: UUID
    about: Optional[str] = None
    domain_id: UUID
    tag_ids: list[UUID] = []
    lifecycle_id: UUID


class RequestInputPortsForDataProductRequest(ORMModel):
    output_ports: list[UUID]
    justification: str


class DataProductCreate(DataProductUpdate):
    owners: Annotated[list[UUID], MinLen(1)]

    input_ports: Optional[RequestInputPortsForDataProductRequest] = None


class DataProductAboutUpdate(ORMModel):
    about: str


class DataProductStatusUpdate(ORMModel):
    status: AbstractDataProductStatus

    @field_validator("status")
    @classmethod
    def status_not_deleting(
        cls, v: AbstractDataProductStatus
    ) -> AbstractDataProductStatus:
        if v == AbstractDataProductStatus.DELETING:
            raise ValueError("Cannot manually set status to 'deleting'")
        return v


class DataProductUsageUpdate(ORMModel):
    usage: str


@deprecated("Use LinkInputPortsToDataProduct")
class LinkDatasetsToDataProduct(ORMModel):
    dataset_ids: list[UUID]
    justification: str


class LinkInputPortsToDataProduct(ORMModel):
    input_ports: list[UUID]
    justification: str
