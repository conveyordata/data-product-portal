from uuid import UUID

from sqlalchemy.orm import Session

from app.data_contracts.model import DataContract as DataContractModel
from app.data_contracts.schema import (
    DataContractCreate,
    DataContractGet,
    QualityScoreUpdate,
)


class DataContractService:
    def get_data_contracts(self, db: Session) -> list[DataContractGet]:
        return db.query(DataContractModel).all()

    def get_data_contract(self, id: UUID, db: Session) -> DataContractGet:
        return db.get(DataContractModel, id)

    def create_data_contract(
        self, data_contract: DataContractCreate, db: Session
    ) -> dict[str, UUID]:
        data_contract = DataContractModel(**data_contract.parse_pydantic_schema())

        db.add(data_contract)
        db.commit()

        return {"id": data_contract.id}

    def delete_data_contract(self, id: UUID, db: Session):
        data_contract = db.get(DataContractModel, id)

        data_contract.columns = []
        data_contract.service_level_objectives = []
        data_contract.delete()
        db.commit()

    def update_quality_score(
        self, id: UUID, new_score: QualityScoreUpdate, db: Session
    ):
        data_contract = db.get(DataContractModel, id)
        data_contract.quality_score = new_score.quality_score
        db.commit()
