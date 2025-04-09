from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DataProductResolver
from app.database.database import get_db_session
from app.dependencies import only_for_admin
from app.domains.schema_create import DomainCreate, DomainUpdate
from app.domains.schema_get import DomainGet, DomainsGet
from app.domains.service import DomainService

router = APIRouter(prefix="/domains", tags=["domains"])


@router.get("")
def get_domains(db: Session = Depends(get_db_session)) -> list[DomainsGet]:
    return DomainService().get_domains(db)


@router.get("/{id}")
def get_domain(id: UUID, db: Session = Depends(get_db_session)) -> DomainGet:
    return DomainService().get_domain(id, db)


@router.post(
    "",
    responses={
        200: {
            "description": "Domain successfully created",
            "content": {
                "application/json": {"example": {"id": "random id of the new domain"}}
            },
        },
    },
    dependencies=[
        Depends(only_for_admin),
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def create_domain(
    domain: DomainCreate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return DomainService().create_domain(domain, db)


@router.put(
    "/{id}",
    dependencies=[
        Depends(only_for_admin),
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def update_domain(
    id: UUID, domain: DomainUpdate, db: Session = Depends(get_db_session)
):
    return DomainService().update_domain(id, domain, db)


@router.delete(
    "/{id}",
    dependencies=[
        Depends(only_for_admin),
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def remove_domain(id: UUID, db: Session = Depends(get_db_session)):
    return DomainService().remove_domain(id, db)


@router.put(
    "/migrate/{from_id}/{to_id}",
    dependencies=[
        Depends(only_for_admin),
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def migrate_domain(from_id: UUID, to_id: UUID, db: Session = Depends(get_db_session)):
    return DomainService().migrate_domain(from_id, to_id, db)
