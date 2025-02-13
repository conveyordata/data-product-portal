from uuid import UUID

from sqlalchemy.orm import Session

from app.data_product_types.model import DataProductType as DataProductTypeModel
from app.data_product_types.schema import DataProductType, DataProductTypeCreate
from app.data_product_types.schema_create import DataProductTypeUpdate


class DataProductTypeService:
    def get_data_product_types(self, db: Session) -> list[DataProductType]:
        return db.query(DataProductTypeModel).order_by(DataProductTypeModel.name).all()

    def create_data_product_type(
        self, data_product_type: DataProductTypeCreate, db: Session
    ) -> dict[str, UUID]:
        data_product_type = DataProductTypeModel(
            **data_product_type.parse_pydantic_schema()
        )
        db.add(data_product_type)
        db.commit()
        return {"id": data_product_type.id}

    def update_data_product_type(
        self, id: UUID, data_product_type: DataProductTypeUpdate, db: Session
    ) -> dict[str, UUID]:
        current_data_product_type = db.get(DataProductTypeModel, id)
        updated_data_product_type = data_product_type.parse_pydantic_schema()

        for attr, value in updated_data_product_type.items():
            setattr(current_data_product_type, attr, value)

        db.commit()
        return {"id": id}

    def remove_data_product_type(self, id: UUID, db: Session):
        data_product_type = db.get(DataProductTypeModel, id)
        db.delete(data_product_type)
        db.commit()
