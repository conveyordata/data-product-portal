from datetime import datetime
from typing import Optional
from uuid import UUID

from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.domains.schema import Domain
from app.data_products.status import DataProductStatus
from app.shared.schema import ORMModel


class EphemeralAccessPortResponse(ORMModel):
    id: UUID
    output_port_id: UUID
    output_port_name: str
    status: DecisionStatus
    data_product_id: UUID

    @classmethod
    def from_link(cls, link: object) -> "EphemeralAccessPortResponse":
        return cls(
            id=link.id,  # type: ignore[attr-defined]
            output_port_id=link.dataset_id,  # type: ignore[attr-defined]
            output_port_name=link.dataset.name,  # type: ignore[attr-defined]
            status=link.status,  # type: ignore[attr-defined]
            data_product_id=link.dataset.data_product_id,  # type: ignore[attr-defined]
        )


class EphemeralAccessResponse(ORMModel):
    id: UUID
    name: str
    description: str
    status: DataProductStatus
    is_ephemeral: bool
    expires_at: Optional[datetime]
    ttl_hours: Optional[int]
    domain: Domain
    input_ports: list[EphemeralAccessPortResponse]

    @classmethod
    def from_model(cls, dp: object) -> "EphemeralAccessResponse":
        return cls(
            id=dp.id,  # type: ignore[attr-defined]
            name=dp.name,  # type: ignore[attr-defined]
            description=dp.description or "",  # type: ignore[attr-defined]
            status=dp.status,  # type: ignore[attr-defined]
            is_ephemeral=dp.is_ephemeral,  # type: ignore[attr-defined]
            expires_at=dp.expires_at,  # type: ignore[attr-defined]
            ttl_hours=dp.ttl_hours,  # type: ignore[attr-defined]
            domain=Domain.model_validate(dp.domain),  # type: ignore[attr-defined]
            input_ports=[
                EphemeralAccessPortResponse.from_link(link)
                for link in dp.dataset_links  # type: ignore[attr-defined]
            ],
        )


class CreateEphemeralAccessResponse(ORMModel):
    id: UUID


class PromoteEphemeralAccessResponse(ORMModel):
    id: UUID
