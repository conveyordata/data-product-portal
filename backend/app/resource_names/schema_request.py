from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.resource_names.enums import ResourceNameModel


class ResourceNameValidationRequest(BaseModel):
    resource_name: str
    data_product_id: Optional[UUID] = None
    model: ResourceNameModel
