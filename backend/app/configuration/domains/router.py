from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.configuration.domains.schema_request import DomainCreate, DomainUpdate
from app.configuration.domains.schema_response import (
    CreateDomainResponse,
    GetDomainResponse,
    GetDomainsResponse,
    UpdateDomainResponse,
)
from app.configuration.domains.service import DomainService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import get_db_session
from app.shared.schema import FinalizerRequest

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
    domain: DomainCreate, db: Session = Depends(get_db_session, scope="function")
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
    id: UUID,
    domain: DomainUpdate,
    db: Session = Depends(get_db_session, scope="function"),
) -> UpdateDomainResponse:
    return DomainService(db).update_domain(id, domain)


@router.delete(
    "/{id}",
    responses={
        200: {"description": "Domain deleted"},
        202: {"description": "Domain marked for deletion, waiting for finalizers"},
    },
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def remove_domain(
    id: UUID, db: Session = Depends(get_db_session, scope="function")
) -> None:
    service = DomainService(db)
    if not service.mark_for_deletion(id):
        return Response(status_code=status.HTTP_202_ACCEPTED)
    service.remove_domain(id)


@router.post(
    "/{id}/finalizers",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__MANAGE_FINALIZERS, EmptyResolver)),
    ],
)
def add_domain_finalizer(
    id: UUID,
    request: FinalizerRequest,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    DomainService(db).add_finalizer(id, request.finalizer)


@router.delete(
    "/{id}/finalizers/{finalizer}",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__MANAGE_FINALIZERS, EmptyResolver)),
    ],
)
def remove_domain_finalizer(
    id: UUID,
    finalizer: str,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    service = DomainService(db)
    if service.remove_finalizer(id, finalizer):
        service.remove_domain(id)


@router.put(
    "/migrate/{from_id}/{to_id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def migrate_domain(
    from_id: UUID, to_id: UUID, db: Session = Depends(get_db_session, scope="function")
) -> None:
    return DomainService(db).migrate_domain(from_id, to_id)


@router.get("")
def get_domains(
    db: Session = Depends(get_db_session, scope="function"),
) -> GetDomainsResponse:
    return GetDomainsResponse(
        domains=DomainService(db).get_domains(),
    )


@router.get("/{id}")
def get_domain(
    id: UUID, db: Session = Depends(get_db_session, scope="function")
) -> GetDomainResponse:
    return DomainService(db).get_domain(id)
