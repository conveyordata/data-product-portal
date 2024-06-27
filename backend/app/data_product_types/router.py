from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data_product_types.schema import DataProductType, DataProductTypeCreate
from app.data_product_types.service import DataProductTypeService
from app.database.database import get_db_session

router = APIRouter(prefix="/data_product_types", tags=["data_product_types"])


@router.get("")
def get_data_products_types(
    db: Session = Depends(get_db_session),
) -> list[DataProductType]:
    return DataProductTypeService().get_data_product_types(db)


@router.post(
    "",
    responses={
        200: {
            "description": "Data Product successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new data product"}
                }
            },
        },
        404: {
            "description": "Owner not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User id for owner not found"}
                }
            },
        },
    },
)
def create_data_product_type(
    data_product_type: DataProductTypeCreate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return DataProductTypeService().create_data_product_type(data_product_type, db)
