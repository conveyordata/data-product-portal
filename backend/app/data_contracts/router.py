from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data_contracts.schema import (
    DataContractCreate,
    DataContractGet,
    QualityScoreUpdate,
)
from app.data_contracts.service import DataContractService
from app.database.database import get_db_session

router = APIRouter(prefix="/data_contracts", tags=["data_contracts"])


@router.get("")
def get_data_contracts(db: Session = Depends(get_db_session)) -> list[DataContractGet]:
    return DataContractService().get_data_contracts(db)


@router.get("/{id}")
def get_data_contract(
    id: UUID, db: Session = Depends(get_db_session)
) -> DataContractGet:
    return DataContractService().get_data_contract(id, db)


@router.post("")
def create_data_contract(
    schema: DataContractCreate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return DataContractService().create_data_contract(schema, db)


@router.delete("/{id}")
def delete_data_contract(id: UUID, db: Session = Depends(get_db_session)):
    return DataContractService().delete_data_contract(id, db)


@router.put("/{id}/score")
def update_quality_score(
    id: UUID, schema: QualityScoreUpdate, db: Session = Depends(get_db_session)
):
    return DataContractService().update_quality_score(id, schema, db)
