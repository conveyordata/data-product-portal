from typing import Optional, Sequence
from uuid import UUID

from pydantic import NaiveDatetime

from app.data_products.output_ports.schema import OutputPort
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.schema import TechnicalAsset
from app.events.enums import EventEntityType
from app.explorations.schema_response import Exploration
from app.shared.schema import ORMModel
from app.users.schema import User
from app.identities.schema import Identity


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
    deleted_actor_identifier: Optional[str] = None
    actor: Optional[User] = None
    data_product: Optional[DataProduct] = None
    user: Optional[User] = None
    output_port: Optional[OutputPort] = None
    technical_asset: Optional[TechnicalAsset] = None
    exploration: Optional[Exploration] = None
    identity: Optional[Identity] = None


class GetEventHistoryResponse(ORMModel):
    events: Sequence[GetEventHistoryResponseItem]
