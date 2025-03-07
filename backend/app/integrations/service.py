from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.model import Integration as IntegrationModel
from app.integrations.schema import Integration


class IntegrationService:
    def __init__(self, db: Session):
        self.db = db

    def get_integrations(self) -> Sequence[Integration]:
        return self.db.scalars(select(IntegrationModel)).all()

    def get_integration(self, uuid: UUID) -> Integration:
        return self.db.scalar(select(IntegrationModel).filter_by(id=uuid))
    
    def create_integration(self, integration: Integration, db: Session) -> dict[str, UUID]:
        integration = IntegrationModel(**integration.parse_pydantic_schema())
        db.add(integration)
        db.commit()
        return {"id": integration.id}

    def delete_integration(self, uuid: UUID, db: Session) -> Integration:
        db_integration = db.scalar(select(IntegrationModel).filter_by(id=uuid))
        if db_integration:
            db.delete(db_integration)
            db.commit()
        return db_integration
