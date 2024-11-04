from uuid import UUID

from sqlalchemy.orm import Session

from app.data_contracts.schema.model import Schema as SchemaModel
from app.data_contracts.schema.schema import SchemaCreate, SchemaGet


class DataContractService:
    def get_schemas(self, db: Session) -> list[SchemaGet]:
        return db.query(SchemaModel).all()

    def get_schema(self, id: UUID, db: Session) -> SchemaGet:
        return db.get(SchemaModel, id)

    def create_schema(self, schema: SchemaCreate, db: Session) -> dict[str, UUID]:
        schema = SchemaModel(**schema.parse_pydantic_schema())

        db.add(schema)
        db.commit()

        return {"id": schema.id}

    def delete_schema(self, id: UUID, db: Session):
        schema = db.get(SchemaModel, id)

        schema.columns = []
        schema.service_level_objectives = []
        schema.delete()
        db.commit()
