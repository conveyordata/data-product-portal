from typing import Optional
from uuid import UUID

from pydantic import NaiveDatetime

from app.data_outputs.schema_response import BaseDataOutputGet
from app.data_products.schema_response import BaseDataProductGet
from app.datasets.schema_response import BaseDatasetGet
from app.domains.schema import Domain
from app.events.enum import Type
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseEventGet(ORMModel):
    id: UUID
    name: str
    subject_id: UUID
    target_id: Optional[UUID] = None
    subject_type: Type
    target_type: Optional[Type] = None
    actor_id: UUID
    domain_id: Optional[UUID] = None
    created_on: NaiveDatetime


class EventGet(BaseEventGet):
    deleted_subject_identifier: Optional[str] = None
    deleted_target_identifier: Optional[str] = None
    actor: User
    data_product: Optional[BaseDataProductGet] = None
    user: Optional[User] = None
    domain: Optional[Domain] = None
    dataset: Optional[BaseDatasetGet] = None
    data_output: Optional[BaseDataOutputGet] = None
