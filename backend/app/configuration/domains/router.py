from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configuration.domains.schema_request import DomainCreate, DomainUpdate
from app.configuration.domains.schema_response import (
    CreateDomainResponse,
    GetDomainResponse,
    GetDomainsItem,
    GetDomainsResponse,
    UpdateDomainResponse,
)
from app.configuration.domains.service import DomainService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session

router = APIRouter(tags=["Configuration - Domains"], prefix="/v2/configuration/domains")


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
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def create_domain(
    domain: DomainCreate, db: Session = Depends(get_db_session)
) -> CreateDomainResponse:
    return DomainService(db).create_domain(domain)


@router.put(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_domain(
    id: UUID, domain: DomainUpdate, db: Session = Depends(get_db_session)
) -> UpdateDomainResponse:
    return DomainService(db).update_domain(id, domain)


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def remove_domain(id: UUID, db: Session = Depends(get_db_session)) -> None:
    return DomainService(db).remove_domain(id)


@router.put(
    "/migrate/{from_id}/{to_id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def migrate_domain(
    from_id: UUID, to_id: UUID, db: Session = Depends(get_db_session)
) -> None:
    return DomainService(db).migrate_domain(from_id, to_id)


@router.get("")
def get_domains(db: Session = Depends(get_db_session)) -> GetDomainsResponse:
    return GetDomainsResponse(
        domains=[
            GetDomainsItem.from_get_domains_item_old(domain)
            for domain in DomainService(db).get_domains()
        ]
    )


@router.get("/{id}")
def get_domain(id: UUID, db: Session = Depends(get_db_session)) -> GetDomainResponse:
    return GetDomainResponse.from_domain_get_old(DomainService(db).get_domain(id))
