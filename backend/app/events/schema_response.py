from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from pydantic import NaiveDatetime

from app.data_products.output_ports.schema import Dataset, OutputPort
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.schema import DataOutput, TechnicalAsset
from app.shared.schema import ORMModel
from app.users.schema import User

from .enums import EventReferenceEntity


class BaseEventGet(ORMModel):
    id: UUID
    name: str
    subject_id: UUID
    target_id: Optional[UUID] = None
    subject_type: EventReferenceEntity
    target_type: Optional[EventReferenceEntity] = None
    actor_id: UUID
    created_on: NaiveDatetime


class GetEventHistoryResponseItem(BaseEventGet):
    deleted_subject_identifier: Optional[str] = None
    deleted_target_identifier: Optional[str] = None
    actor: User
    data_product: Optional[DataProduct] = None
    user: Optional[User] = None
    output_port: Optional[OutputPort] = None
    technical_asset: Optional[TechnicalAsset] = None


@deprecated("Use GetEventHistoryResponseItem instead")
class GetEventHistoryResponseItemOld(BaseEventGet):
    deleted_subject_identifier: Optional[str] = None
    deleted_target_identifier: Optional[str] = None
    actor: User
    data_product: Optional[DataProduct] = None
    user: Optional[User] = None
    dataset: Optional[Dataset] = None
    data_output: Optional[DataOutput] = None

    def convert(self) -> GetEventHistoryResponseItem:
        return GetEventHistoryResponseItem(
            **self.model_dump(exclude={"dataset", "data_output"}),
            output_port=self.dataset.convert() if self.dataset is not None else None,
            technical_asset=self.data_output.convert()
            if self.data_output is not None
            else None,
        )


class GetEventHistoryResponse(ORMModel):
    events: Sequence[GetEventHistoryResponseItem]
