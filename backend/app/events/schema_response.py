from enum import UNIQUE, Enum, verify
from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from pydantic import NaiveDatetime

from app.data_products.output_ports.schema import Dataset, OutputPort
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.schema import TechnicalAsset
from app.shared.schema import ORMModel
from app.users.schema import User

from .enums import EventReferenceEntity as EventReferenceEntityOld


@verify(UNIQUE)
class EventEntityType(str, Enum):
    DATA_PRODUCT = "data_product"
    OUTPUT_PORT = "output_port"
    TECHNICAL_ASSET = "technical_asset"
    USER = "user"

    @staticmethod
    def from_old(old: EventReferenceEntityOld) -> "EventEntityType":
        match old:
            case EventReferenceEntityOld.DATA_PRODUCT:
                return EventEntityType.DATA_PRODUCT
            case EventReferenceEntityOld.DATASET:
                return EventEntityType.OUTPUT_PORT
            case EventReferenceEntityOld.DATA_OUTPUT:
                return EventEntityType.TECHNICAL_ASSET
            case EventReferenceEntityOld.USER:
                return EventEntityType.USER


class GetEventHistoryResponseItem(ORMModel):
    id: UUID
    name: str
    subject_id: UUID
    target_id: Optional[UUID] = None
    subject_type: EventEntityType
    target_type: Optional[EventEntityType] = None
    actor_id: UUID
    created_on: NaiveDatetime
    deleted_subject_identifier: Optional[str] = None
    deleted_target_identifier: Optional[str] = None
    actor: User
    data_product: Optional[DataProduct] = None
    user: Optional[User] = None
    output_port: Optional[OutputPort] = None
    technical_asset: Optional[TechnicalAsset] = None


@deprecated("Use GetEventHistoryResponseItem instead")
class GetEventHistoryResponseItemOld(ORMModel):
    id: UUID
    name: str
    subject_id: UUID
    target_id: Optional[UUID] = None
    subject_type: EventReferenceEntityOld
    target_type: Optional[EventReferenceEntityOld] = None
    actor_id: UUID
    created_on: NaiveDatetime
    deleted_subject_identifier: Optional[str] = None
    deleted_target_identifier: Optional[str] = None
    actor: User
    data_product: Optional[DataProduct] = None
    user: Optional[User] = None
    dataset: Optional[Dataset] = None
    data_output: Optional[TechnicalAsset] = None

    def convert(self) -> GetEventHistoryResponseItem:
        return GetEventHistoryResponseItem(
            **self.model_dump(
                exclude={"dataset", "data_output", "subject_type", "target_type"}
            ),
            output_port=self.dataset.convert() if self.dataset is not None else None,
            technical_asset=self.data_output.convert()
            if self.data_output is not None
            else None,
            subject_type=EventEntityType.from_old(self.subject_type),
            target_type=EventEntityType.from_old(self.target_type)
            if self.target_type is not None
            else None,
        )


class GetEventHistoryResponse(ORMModel):
    events: Sequence[GetEventHistoryResponseItem]
