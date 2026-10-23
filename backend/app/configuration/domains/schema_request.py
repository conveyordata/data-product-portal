from app.configuration.domains.model import Domain as DomainModel
from app.shared.schema import ORMModel


class DomainUpdate(ORMModel):
    name: str
    description: str

    class Meta:
        orm_model = DomainModel


class DomainCreate(DomainUpdate):
    namespace: str
