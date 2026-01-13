from abc import ABC
from typing import Type, TypeAlias, Union, cast

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.output_port.model import DatasetRoleAssignment
from app.data_products.model import DataProduct
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation,
)
from app.data_products.output_ports.input_ports.model import (
    DataProductDatasetAssociation,
)
from app.data_products.output_ports.model import Dataset
from app.data_products.technical_assets.model import DataOutput
from app.database.database import get_db_session

Model: TypeAlias = Union[Type[DataProduct], Type[Dataset], Type[DataOutput], None]


class SubjectResolver(ABC):
    DEFAULT: str = "*"
    model: Model = None

    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        if (result := request.query_params.get(key)) is not None:
            return cast("str", result)
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


class DatasetRoleAssignmentResolver(SubjectResolver):
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
                return assignment.dataset_id
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


class DatasetResolver(SubjectResolver):
    model: Model = Dataset

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


class DataOutputResolver(SubjectResolver):
    model: Model = DataProduct

    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        obj = await DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_output = (
                db.scalars(select(DataOutput).where(DataOutput.id == obj))
                .unique()
                .one_or_none()
            )
            if data_output:
                return data_output.owner_id
        return cls.DEFAULT


class DataOutputDatasetAssociationResolver(DatasetResolver):
    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        obj = await SubjectResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_output_dataset = db.scalar(
                select(DataOutputDatasetAssociation).where(
                    DataOutputDatasetAssociation.id == obj
                )
            )
            if data_output_dataset:
                return data_output_dataset.dataset_id
        return cls.DEFAULT


class DataProductDatasetAssociationResolver(DatasetResolver):
    @classmethod
    async def resolve(
        cls, request: Request, key: str, db: Session = Depends(get_db_session)
    ):
        obj = await DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_product_dataset = (
                db.scalars(
                    select(DataProductDatasetAssociation).where(
                        DataProductDatasetAssociation.id == obj
                    )
                )
                .unique()
                .one_or_none()
            )
            if data_product_dataset:
                return data_product_dataset.dataset_id
        return cls.DEFAULT
