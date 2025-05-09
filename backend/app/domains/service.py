from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.domains.model import Domain as DomainModel
from app.domains.model import ensure_domain_exists
from app.domains.schema_request import DomainCreate, DomainUpdate
from app.domains.schema_response import DomainGet, DomainsGet


class DomainService:
    def get_domains(self, db: Session) -> list[DomainsGet]:
        return (
            db.scalars(
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

    def get_domain(self, id: UUID, db: Session) -> DomainGet:
        domain = db.get(
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

    def create_domain(self, domain: DomainCreate, db: Session) -> dict[str, UUID]:
        domain = DomainModel(**domain.parse_pydantic_schema())
        db.add(domain)
        db.commit()
        return {"id": domain.id}

    def update_domain(
        self, id: UUID, domain: DomainUpdate, db: Session
    ) -> dict[str, UUID]:
        current_domain = db.get(DomainModel, id)
        updated_domain = domain.parse_pydantic_schema()

        for attr, value in updated_domain.items():
            setattr(current_domain, attr, value)

        db.commit()
        return {"id": id}

    def remove_domain(self, id: UUID, db: Session):
        domain = db.get(
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

        db.delete(domain)
        db.commit()

    def migrate_domain(self, from_id: UUID, to_id: UUID, db: Session):
        domain = ensure_domain_exists(
            from_id,
            db,
            options=[
                joinedload(DomainModel.datasets),
                joinedload(DomainModel.data_products),
            ],
        )
        new_domain = ensure_domain_exists(to_id, db)

        for dataset in domain.datasets:
            dataset.domain_id = new_domain.id

        for data_product in domain.data_products:
            data_product.domain_id = new_domain.id

        db.commit()
