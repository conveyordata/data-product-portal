from app.domains.model import Domain as DomainModel
from app.shared.schema import ORMModel


class DomainCreate(ORMModel):
    name: str
    description: str

    class Meta:
        orm_model = DomainModel


class DomainUpdate(DomainCreate):
    pass
