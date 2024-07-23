from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data_outputs.schema import DataOutput, DataOutputCreate
from app.data_outputs.service import DataOutputService
from app.database.database import get_db_session

router = APIRouter(prefix="/data_outputs", tags=["data_outputs"])


@router.get("")
def get_data_outputs(db: Session = Depends(get_db_session)) -> list[DataOutput]:
    return DataOutputService().get_data_outputs(db)


@router.get("/{id}")
def get_data_output(id: UUID, db: Session = Depends(get_db_session)) -> DataOutput:
    return DataOutputService().get_data_output(id, db)


@router.post(
    "",
    responses={
        200: {
            "description": "DataOutput successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new data_output"}
                }
            },
        },
    },
)
def create_data_output(
    data_output: DataOutputCreate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return DataOutputService().create_data_output(data_output, db)
