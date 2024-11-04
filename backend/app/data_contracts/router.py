from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data_contracts.schema.schema import SchemaCreate, SchemaGet
from app.data_contracts.service import DataContractService
from app.database.database import get_db_session

router = APIRouter(prefix="/data_contracts", tags=["data_contracts"])


@router.get("")
def get_schemas(db: Session = Depends(get_db_session)) -> list[SchemaGet]:
    return DataContractService().get_schemas(db)


@router.get("/{id}")
def get_schema(id: UUID, db: Session = Depends(get_db_session)) -> SchemaGet:
    return DataContractService().get_schema(id, db)


@router.post("")
def create_schema(
    schema: SchemaCreate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return DataContractService().create_schema(schema, db)


@router.delete("/{id}")
def remove_schema(id: UUID, db: Session = Depends(get_db_session)):
    return DataContractService().delete_schema(id, db)
