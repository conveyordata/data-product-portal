from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.data_product_types.model import DataProductType as DataProductTypeModel
from app.data_product_types.model import ensure_data_product_type_exists
from app.data_product_types.schema_request import (
    DataProductTypeCreate,
    DataProductTypeUpdate,
)
from app.data_product_types.schema_response import (
    DataProductTypeGet,
    DataProductTypesGet,
)


class DataProductTypeService:
    def __init__(self, db: Session):
        self.db = db

    def get_data_product_types(self) -> Sequence[DataProductTypesGet]:
        return (
            self.db.scalars(
                select(DataProductTypeModel)
                .options(joinedload(DataProductTypeModel.data_products))
                .order_by(DataProductTypeModel.name)
            )
            .unique()
            .all()
        )

    def get_data_product_type(self, id: UUID) -> DataProductTypeGet:
        data_product_type = self.db.get(
            DataProductTypeModel,
            id,
            options=[joinedload(DataProductTypeModel.data_products)],
        )

        if not data_product_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data product type not found",
            )

        return data_product_type

    def create_data_product_type(
        self, data_product_type: DataProductTypeCreate
    ) -> dict[str, UUID]:
        data_product_type = DataProductTypeModel(
            **data_product_type.parse_pydantic_schema()
        )
        self.db.add(data_product_type)
        self.db.commit()
        return {"id": data_product_type.id}

    def update_data_product_type(
        self, id: UUID, data_product_type: DataProductTypeUpdate
    ) -> dict[str, UUID]:
        current_data_product_type = self.db.get(DataProductTypeModel, id)
        updated_data_product_type = data_product_type.parse_pydantic_schema()

        for attr, value in updated_data_product_type.items():
            setattr(current_data_product_type, attr, value)

        self.db.commit()
        return {"id": id}

    def remove_data_product_type(self, id: UUID) -> None:
        data_product_type = self.db.get(
            DataProductTypeModel,
            id,
            options=[joinedload(DataProductTypeModel.data_products)],
        )

        if data_product_type.data_products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Cannot delete a data product type assigned to one or "
                    "multiple data products"
                ),
            )

        self.db.delete(data_product_type)
        self.db.commit()

    def migrate_data_product_type(self, from_id: UUID, to_id: UUID) -> None:
        data_product_type = ensure_data_product_type_exists(
            from_id,
            self.db,
            options=[joinedload(DataProductTypeModel.data_products)],
        )
        new_data_product_type = ensure_data_product_type_exists(to_id, self.db)

        for data_product in data_product_type.data_products:
            data_product.type_id = new_data_product_type.id

        self.db.commit()
