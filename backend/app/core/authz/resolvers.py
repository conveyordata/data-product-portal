from abc import ABC
from typing import Type, TypeAlias, Union, cast

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.abstract_data_product.input_ports.model import (
    InputPort,
)
from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignment,
)
from app.data_products.model import DataProduct
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation,
)
from app.data_products.output_ports.model import OutputPort
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.deps import get_db_session
from app.explorations.model import Exploration

Model: TypeAlias = Union[
    Type[DataProduct], Type[OutputPort], Type[TechnicalAsset], None
]


class SubjectResolver(ABC):
    DEFAULT: str = "*"
    model: Model = None

    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        if (result := request.query_params.get(key)) is not None:
            return result
        if (result := request.path_params.get(key)) is not None:
            return cast("str", result)
        json_body = await request.json()
        if isinstance(json_body, dict) and (result := json_body.get(key)) is not None:
            return cast("str", result)

        return cls.DEFAULT

    @classmethod
    async def resolve_domain(
        cls,
        db: Session,
        id_: str,
    ) -> str:
        if id_ == cls.DEFAULT or cls.model is None:
            return cls.DEFAULT
        domain = db.scalar(select(cls.model.domain_id).where(cls.model.id == id_))
        return cls.DEFAULT if domain is None else str(domain)


class EmptyResolver(SubjectResolver):
    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        return cls.DEFAULT


class DataProductResolver(SubjectResolver):
    model: Model = DataProduct


class ExplorationResolver(SubjectResolver):
    model: Model = Exploration


class OutputPortRoleAssignmentResolver(SubjectResolver):
    model: Model = DataProduct

    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        obj = await DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            assignment = (
                db.scalars(
                    select(DatasetRoleAssignment).where(DatasetRoleAssignment.id == obj)
                )
                .unique()
                .one_or_none()
            )
            if assignment:
                return assignment.output_port_id
        return cls.DEFAULT


class DataProductRoleAssignmentResolver(SubjectResolver):
    model: Model = DataProduct

    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        obj = await DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            assignment = (
                db.scalars(
                    select(DataProductRoleAssignment).where(
                        DataProductRoleAssignment.id == obj
                    )
                )
                .unique()
                .one_or_none()
            )
            if assignment:
                return assignment.data_product_id
        return cls.DEFAULT


class OutputPortResolver(SubjectResolver):
    model: Model = OutputPort

    @classmethod
    async def resolve_domain(
        cls,
        db: Session,
        id_: str,
    ) -> str:
        if id_ == cls.DEFAULT or cls.model is None:
            return cls.DEFAULT
        domain = db.scalar(
            select(DataProduct.domain_id).join(cls.model).where(cls.model.id == id_)
        )
        return cls.DEFAULT if domain is None else str(domain)


class DataProductNameResolver(SubjectResolver):
    model: Model = DataProduct

    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        obj = await DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_product = (
                db.scalars(select(DataProduct).where(DataProduct.namespace == obj))
                .unique()
                .one_or_none()
            )
            if data_product:
                return data_product.id
        return cls.DEFAULT


class TechnicalAssetResolver(SubjectResolver):
    model: Model = DataProduct

    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        obj = await DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            technical_asset = (
                db.scalars(select(TechnicalAsset).where(TechnicalAsset.id == obj))
                .unique()
                .one_or_none()
            )
            if technical_asset:
                return technical_asset.owner_id
        return cls.DEFAULT


class TechnicalAssetOutputPortAssociationResolver(OutputPortResolver):
    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        obj = await SubjectResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            technical_asset_output_port = db.scalar(
                select(DataOutputDatasetAssociation).where(
                    DataOutputDatasetAssociation.id == obj
                )
            )
            if technical_asset_output_port:
                return technical_asset_output_port.output_port_id
        return cls.DEFAULT


class DataProductOutputPortAssociationResolver(OutputPortResolver):
    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        obj = await DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_product_dataset = (
                db.scalars(select(InputPort).where(InputPort.id == obj))
                .unique()
                .one_or_none()
            )
            if data_product_dataset:
                return data_product_dataset.output_port_id
        return cls.DEFAULT
