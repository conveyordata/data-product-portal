from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.domains.model import Domain as DomainModel
from app.domains.model import ensure_domain_exists
from app.domains.schema_request import DomainCreate, DomainUpdate
from app.domains.schema_response import DomainGet, DomainsGet


class DomainService:
    def __init__(self, db: Session):
        self.db = db

    def get_domains(self) -> Sequence[DomainsGet]:
        return (
            self.db.scalars(
                select(DomainModel)
                .options(
                    joinedload(DomainModel.datasets),
                    joinedload(DomainModel.data_products),
                )
                .order_by(DomainModel.name)
            )
            .unique()
            .all()
        )

    def get_domain(self, id: UUID) -> DomainGet:
        domain = self.db.get(
            DomainModel,
            id,
            options=[
                joinedload(DomainModel.datasets),
                joinedload(DomainModel.data_products),
            ],
        )

        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found",
            )

        return domain

    def create_domain(self, domain: DomainCreate) -> dict[str, UUID]:
        domain = DomainModel(**domain.parse_pydantic_schema())
        self.db.add(domain)
        self.db.commit()
        return {"id": domain.id}

    def update_domain(self, id: UUID, domain: DomainUpdate) -> dict[str, UUID]:
        current_domain = self.db.get(DomainModel, id)
        updated_domain = domain.parse_pydantic_schema()

        for attr, value in updated_domain.items():
            setattr(current_domain, attr, value)

        self.db.commit()
        return {"id": id}

    def remove_domain(self, id: UUID) -> None:
        domain = self.db.get(
            DomainModel,
            id,
            options=[
                joinedload(DomainModel.datasets),
                joinedload(DomainModel.data_products),
            ],
        )

        if domain.data_products or domain.datasets:
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
                joinedload(DomainModel.datasets),
                joinedload(DomainModel.data_products),
            ],
        )
        new_domain = ensure_domain_exists(to_id, self.db)

        for dataset in domain.datasets:
            dataset.domain_id = new_domain.id

        for data_product in domain.data_products:
            data_product.domain_id = new_domain.id

        self.db.commit()
