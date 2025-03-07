from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.integrations.schema import Integration
from app.integrations.service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("")
def get_integrations(db: Session = Depends(get_db_session)) -> Sequence[Integration]:
    return IntegrationService(db).get_integrations()

@router.get("/{id}")
def get_integration(uuid: UUID, db: Session = Depends(get_db_session)) -> Integration:
    return IntegrationService(db).get_integration(uuid)

@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "Integration not found",
            "content": {
                "application/json": {"example": {"detail": "UUID not found"}}
            },
        }
    },
)
def remove_integration(uuid: UUID, db: Session = Depends(get_db_session)) -> None:
    return IntegrationService().remove_integration(uuid, db)

@router.post(
    "",
    responses={
        200: {
            "description": "Integration successfully created",
            "content": {
                "application/json": {"example": {"id": "random id of the new user"}}
            },
        },
    },
)
def create_integration(
    integration: Integration, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return IntegrationService().create_integration(integration, db)