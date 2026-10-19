from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session, selectinload

from app.abstract_data_product.model import AbstractDataProduct
from app.configuration.domains.model import Domain as DomainModel
from app.configuration.domains.model import ensure_domain_exists
from app.configuration.domains.schema_request import DomainCreate, DomainUpdate
from app.configuration.domains.schema_response import (
    CreateDomainResponse,
    GetDomainResponse,
    GetDomainsItem,
    UpdateDomainResponse,
)
from app.configuration.domains.status import DomainStatus
from app.core.namespace.validation import NamespaceValidator
from app.database.database import UNFILTERED
from app.resource_names.service import ResourceNameValidityType


class DomainService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = NamespaceValidator(DomainModel)

    def get_domains(self) -> Sequence[GetDomainsItem]:
        counts = dict(
            self.db.execute(
                select(
                    DomainModel.id,
                    func.count(AbstractDataProduct.id),
                )
                .outerjoin(
                    AbstractDataProduct,
                    AbstractDataProduct.domain_id == DomainModel.id,
                )
                .group_by(DomainModel.id),
                execution_options=UNFILTERED,
            ).all()
        )

        domains = self.db.scalars(select(DomainModel).order_by(DomainModel.name)).all()
        return [
            GetDomainsItem(
                id=domain.id,
                name=domain.name,
                namespace=domain.namespace,
                description=domain.description,
                status=domain.status,
                finalizers=domain.finalizers,
                abstract_data_product_count=counts.get(domain.id, 0),
            )
            for domain in domains
        ]

    def get_domain(self, id: UUID) -> GetDomainResponse:
        domain = self.db.get(DomainModel, id)

        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found",
            )

        return domain

    def _ensure_not_deleting(self, domain: DomainModel) -> None:
        if domain.status == DomainStatus.DELETING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Domain '{domain.name}' is pending deletion and cannot be used or modified",
            )

    def ensure_assignable(self, id: UUID) -> None:
        self._ensure_not_deleting(ensure_domain_exists(id, self.db))

    def create_domain(self, domain_create: DomainCreate) -> CreateDomainResponse:
        if (
            validity := self.namespace_validator.validate_namespace(
                domain_create.namespace, self.db
            ).validity
        ) != ResourceNameValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )
        domain_schema = domain_create.model_dump(exclude={"environment_ids"})
        domain = DomainModel(**domain_schema)
        self.db.add(domain)
        self.db.flush()
        return CreateDomainResponse(id=domain.id)

    def update_domain(self, id: UUID, domain: DomainUpdate) -> UpdateDomainResponse:
        current_domain = ensure_domain_exists(
            id, self.db, options=[selectinload(DomainModel.environments)]
        )
        self._ensure_not_deleting(current_domain)
        updated_domain = domain.model_dump()

        for attr, value in updated_domain.items():
            setattr(current_domain, attr, value)

        self.db.flush()
        return UpdateDomainResponse(id=id)

    def mark_for_deletion(self, id: UUID) -> bool:
        domain = ensure_domain_exists(id, self.db)
        self._ensure_no_data_products(id)
        if not domain.finalizers:
            return True
        domain.status = DomainStatus.DELETING
        self.db.flush()
        return False

    def add_finalizer(self, id: UUID, finalizer: str) -> None:
        domain = ensure_domain_exists(id, self.db)
        self._ensure_not_deleting(domain)
        if finalizer in domain.finalizers:
            return
        domain.finalizers = [*domain.finalizers, finalizer]
        self.db.flush()

    def remove_finalizer(self, id: UUID, finalizer: str) -> bool:
        domain = ensure_domain_exists(id, self.db)
        if finalizer not in domain.finalizers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Finalizer '{finalizer}' not found",
            )
        domain.finalizers = [f for f in domain.finalizers if f != finalizer]
        self.db.flush()
        should_delete = domain.status == DomainStatus.DELETING and not domain.finalizers
        if should_delete:
            self._ensure_no_data_products(id)
        return should_delete

    def _ensure_no_data_products(self, id: UUID) -> None:
        if self.db.scalar(
            select(exists().where(AbstractDataProduct.domain_id == id)),
            execution_options=UNFILTERED,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete a domain that still has data products or explorations",
            )

    def remove_domain(self, id: UUID) -> None:
        self.db.delete(ensure_domain_exists(id, self.db))
        self.db.flush()

    def migrate_domain(self, from_id: UUID, to_id: UUID) -> None:
        domain = ensure_domain_exists(
            from_id,
            self.db,
            options=[
                selectinload(DomainModel.abstract_data_products),
            ],
            execution_options=UNFILTERED,
        )
        new_domain = ensure_domain_exists(to_id, self.db)
        self._ensure_not_deleting(new_domain)

        for data_product in domain.abstract_data_products:
            data_product.domain_id = new_domain.id

        self.db.flush()
