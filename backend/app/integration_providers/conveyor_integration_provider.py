from uuid import UUID

from sqlalchemy.orm import Session

from app.core.conveyor.notebook_builder import CONVEYOR_SERVICE
from app.data_products.model import DataProduct as DataProductModel
from app.integration_providers.integration_provider import IntegrationProvider
from app.users.schema import User


class ConveyorIntegrationProvider(IntegrationProvider):
    def __init__(self, db: Session):
        super().__init__(db)

    def generate_url(self, id: UUID, environment: str, actor: User) -> str:
        dp = self.db.get(DataProductModel, id)
        return CONVEYOR_SERVICE.generate_ide_url(dp.namespace)
