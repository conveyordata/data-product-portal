import uuid as uuid_module
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.configuration.data_product_types.enums import DataProductIconKey
from app.configuration.data_product_types.model import DataProductType
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import ensure_data_product_exists
from app.data_products.output_ports.input_ports.model import (
    DataProductDatasetAssociation,
)
from app.data_products.output_ports.model import Dataset as DatasetModel
from app.data_products.service import DataProductService
from app.data_products.status import DataProductStatus
from app.ephemeral_access.schema_request import EphemeralDataProductCreate
from app.users.schema import User


class EphemeralAccessService:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_ephemeral_type(self) -> DataProductType:
        type_ = self.db.scalar(
            select(DataProductType).filter(DataProductType.name == "Ephemeral")
        )
        if not type_:
            type_ = DataProductType(
                name="Ephemeral",
                description="Auto-created type for temporary data access requests",
                icon_key=DataProductIconKey.EXPLORATION,
            )
            self.db.add(type_)
            self.db.flush()
        return type_

    _ADJECTIVES = [
        "agile",
        "bold",
        "calm",
        "dark",
        "eager",
        "fast",
        "gold",
        "happy",
        "icy",
        "jade",
        "keen",
        "lush",
        "misty",
        "neat",
        "open",
        "pure",
        "quick",
        "rich",
        "soft",
        "teal",
    ]
    _NOUNS = [
        "atlas",
        "brook",
        "cloud",
        "delta",
        "echo",
        "fjord",
        "grove",
        "haven",
        "inlet",
        "jetty",
        "knoll",
        "locus",
        "mesa",
        "nexus",
        "oasis",
        "peak",
        "quest",
        "ridge",
        "shore",
        "trail",
    ]

    def _generate_name_and_namespace(self, name: Optional[str]) -> tuple[str, str]:
        import secrets

        if name:
            display_name = name[:80]
        else:
            adj = secrets.choice(self._ADJECTIVES)
            noun = secrets.choice(self._NOUNS)
            display_name = f"Exploration {adj}-{noun}"
        namespace = f"exploration_{str(uuid_module.uuid4())[:8]}"
        return display_name, namespace

    def create_ephemeral_access(
        self,
        data: EphemeralDataProductCreate,
        actor: User,
    ) -> DataProductModel:
        ephemeral_type = self._get_or_create_ephemeral_type()

        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )

        first_port = self.db.get(DatasetModel, data.output_port_ids[0])
        if not first_port:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Output port not found",
            )
        parent_dp = self.db.get(DataProductModel, first_port.data_product_id)
        if not parent_dp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent data product not found",
            )

        name, namespace = self._generate_name_and_namespace(data.name)
        expires_at = datetime.now(tz=pytz.utc) + timedelta(hours=data.ttl_hours)

        dp = DataProductModel(
            name=name,
            namespace=namespace,
            description=data.justification or "",
            is_ephemeral=True,
            expires_at=expires_at,
            ttl_hours=data.ttl_hours,
            type_id=ephemeral_type.id,
            domain_id=parent_dp.domain_id,
            lifecycle_id=default_lifecycle.id if default_lifecycle else None,
            status=DataProductStatus.ACTIVE,
            tags=[],
        )
        self.db.add(dp)
        self.db.commit()
        return dp

    def list_ephemeral_access(self, user_id: UUID) -> list[DataProductModel]:
        return (
            self.db.scalars(
                select(DataProductModel)
                .options(
                    selectinload(DataProductModel.dataset_links).selectinload(
                        DataProductDatasetAssociation.dataset
                    ),
                    selectinload(DataProductModel.assignments).raiseload("*"),
                )
                .where(DataProductModel.is_ephemeral == True)  # noqa: E712
                .where(
                    DataProductModel.assignments.any(
                        user_id=user_id,
                        decision=DecisionStatus.APPROVED,
                    )
                )
                .order_by(DataProductModel.expires_at)
            )
            .unique()
            .all()
        )

    def add_output_ports(
        self,
        ephemeral_id: UUID,
        output_port_ids: list[UUID],
        actor: User,
    ) -> None:
        dp = ensure_data_product_exists(ephemeral_id, self.db)
        if not dp.is_ephemeral:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data product is not ephemeral",
            )
        DataProductService(self.db).link_datasets_to_data_product(
            ephemeral_id,
            output_port_ids,
            justification=f"Added to exploration {dp.name}",
            actor=actor,
        )

    def revoke_ephemeral_access(self, ephemeral_id: UUID) -> None:
        dp = ensure_data_product_exists(ephemeral_id, self.db)
        if not dp.is_ephemeral:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data product is not ephemeral",
            )
        dp.status = DataProductStatus.ARCHIVED
        self.db.commit()

    def promote_ephemeral_access(self, ephemeral_id: UUID) -> UUID:
        dp = ensure_data_product_exists(ephemeral_id, self.db)
        if not dp.is_ephemeral:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data product is not ephemeral",
            )
        dp.is_ephemeral = False
        dp.expires_at = None
        dp.ttl_hours = None
        self.db.commit()
        return dp.id
