from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, undefer

from app.configuration.domains.model import Domain as DomainModel
from app.configuration.domains.model import ensure_domain_exists
from app.configuration.domains.schema_request import DomainCreate, DomainUpdate
from app.configuration.domains.schema_response import (
    CreateDomainResponse,
    GetDomainResponse,
    GetDomainsItem,
    UpdateDomainResponse,
)
from app.configuration.environments.model import Environment as EnvironmentModel


class DomainService:
    def __init__(self, db: Session):
        self.db = db

    def get_domains(self) -> Sequence[GetDomainsItem]:
        return (
            self.db.scalars(
                select(DomainModel)
                .options(
                    undefer(DomainModel.abstract_data_product_count),
                    selectinload(DomainModel.environments),
                )
                .order_by(DomainModel.name)
            )
            .unique()
            .all()
        )

    def get_domain(self, id: UUID) -> GetDomainResponse:
        domain = self.db.get(
            DomainModel,
            id,
            options=[
                undefer(DomainModel.abstract_data_product_count),
                selectinload(DomainModel.environments),
            ],
        )

        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found",
            )

        return domain

    def _get_environments(self, environment_ids: list[UUID]) -> list[EnvironmentModel]:
        environments = self.db.scalars(
            select(EnvironmentModel).where(EnvironmentModel.id.in_(environment_ids))
        ).all()
        if len(environment_ids) != len(environments):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid environment ids provided",
            )
        return list(environments)

    def create_domain(self, domain_create: DomainCreate) -> CreateDomainResponse:
        domain_schema = domain_create.model_dump(exclude={"environment_ids"})
        environments = self._get_environments(domain_create.environment_ids)
        domain = DomainModel(**domain_schema, environments=environments)
        self.db.add(domain)
        self.db.commit()
        return CreateDomainResponse(id=domain.id)

    def update_domain(self, id: UUID, domain: DomainUpdate) -> UpdateDomainResponse:
        current_domain = self.db.get(
            DomainModel, id, options=[selectinload(DomainModel.environments)]
        )
        updated_domain = domain.model_dump()

        environment_ids = updated_domain.pop("environment_ids")
        current_domain.environments = self._get_environments(environment_ids)

        for attr, value in updated_domain.items():
            setattr(current_domain, attr, value)

        self.db.commit()
        return UpdateDomainResponse(id=id)

    def remove_domain(self, id: UUID) -> None:
        domain = self.db.get(
            DomainModel,
            id,
            options=[
                selectinload(DomainModel.abstract_data_products),
            ],
        )
        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found",
            )

        if domain.abstract_data_products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Cannot delete a domain assigned to one or multiple "
                    "data products or datasets"
                ),
            )

        self.db.delete(domain)
        self.db.commit()

    def migrate_domain(self, from_id: UUID, to_id: UUID) -> None:
        domain = ensure_domain_exists(
            from_id,
            self.db,
            options=[
                selectinload(DomainModel.abstract_data_products),
            ],
        )
        new_domain = ensure_domain_exists(to_id, self.db)

        for data_product in domain.abstract_data_products:
            data_product.domain_id = new_domain.id

        self.db.commit()
