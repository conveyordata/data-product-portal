from abc import ABC
from typing import Type, TypeAlias, Union, cast

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data_outputs.model import DataOutput
from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_products.model import DataProduct
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import get_db_session
from app.datasets.model import Dataset

Model: TypeAlias = Union[Type[DataProduct], Type[Dataset], Type[DataOutput], None]


class SubjectResolver(ABC):
    DEFAULT: str = "*"
    model: Model = None

    @classmethod
    def resolve(cls, request: Request, key: str, db: Session = Depends(get_db_session)):
        if (result := request.query_params.get(key)) is not None:
            return cast(str, result)
        if (result := request.path_params.get(key)) is not None:
            return cast(str, result)
        return cls.DEFAULT

    @classmethod
    def resolve_domain(
        cls,
        db: Session,
        id_: str,
    ) -> str:
        if id_ == cls.DEFAULT or cls.model is None:
            return cls.DEFAULT
        domain = db.scalars(
            select(cls.model.domain_id).where(cls.model.id == id_)
        ).one_or_none()
        return cls.DEFAULT if domain is None else str(domain)


class DataProductResolver(SubjectResolver):
    model: Model = DataProduct


class DatasetResolver(SubjectResolver):
    model: Model = Dataset


class DataProductNameResolver(SubjectResolver):
    model: Model = DataProduct

    @classmethod
    def resolve(cls, request: Request, key: str, db: Session = Depends(get_db_session)):
        obj = DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_product = (
                db.scalars(select(DataProduct).where(DataProduct.name == obj))
                .unique()
                .one_or_none()
            )
            if data_product:
                return data_product.id
        return cls.DEFAULT


class DataOutputResolver(SubjectResolver):
    model: Model = DataProduct

    @classmethod
    def resolve(cls, request: Request, key: str, db: Session = Depends(get_db_session)):
        obj = DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_output = (
                db.scalars(select(DataOutput).where(DataOutput.id == obj))
                .unique()
                .one_or_none()
            )
            if data_output:
                return data_output.owner_id
        return cls.DEFAULT


class DataOutputDatasetAssociationResolver(SubjectResolver):
    model: Model = Dataset

    @classmethod
    def resolve(cls, request: Request, key: str, db: Session = Depends(get_db_session)):
        obj = DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_output_dataset = (
                db.scalars(
                    select(DataOutputDatasetAssociation).where(
                        DataOutputDatasetAssociation.id == obj
                    )
                )
                .unique()
                .one_or_none()
            )
            if data_output_dataset:
                return data_output_dataset.dataset_id
        return cls.DEFAULT


class DataProductDatasetAssociationResolver(SubjectResolver):
    model: Model = Dataset

    @classmethod
    def resolve(cls, request: Request, key: str, db: Session = Depends(get_db_session)):
        obj = DataProductResolver.resolve(request, key, db)
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
