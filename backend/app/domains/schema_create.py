from pydantic import Field

from app.domains.model import Domain as DomainModel
from app.shared.schema import ORMModel


class DomainCreate(ORMModel):
    name: str = Field(..., description="Name of the domain")
    description: str = Field(..., description="Description of the domain")

    class Meta:
        orm_model = DomainModel


class DomainUpdate(DomainCreate):
    pass
