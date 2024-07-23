from uuid import UUID

from sqlalchemy.orm import Session

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_outputs.schema import DataOutput, DataOutputCreate, DataOutputToDB
from app.data_outputs.schema_union import DataOutputMap


class DataOutputService:
    def get_data_outputs(self, db: Session) -> list[DataOutput]:
        data_outputs = db.query(DataOutputModel).all()
        parsed_data_outputs = []
        for data_output in data_outputs:
            parsed_data_output = data_output
            parsed_data_output.configuration = DataOutputMap[
                data_output.configuration_type
            ].model_validate_json(data_output.configuration)
            parsed_data_outputs.append(parsed_data_output)
        return parsed_data_outputs

    def get_data_output(self, id: UUID, db: Session) -> DataOutput:
        return db.query(DataOutputModel).filter(DataOutput.id == id).first()

    def create_data_output(
        self, data_output: DataOutputCreate, db: Session
    ) -> dict[str, UUID]:
        data_output = DataOutputToDB(
            name=data_output.name,
            owner_id=data_output.owner_id,
            configuration=data_output.configuration.model_dump_json(),
            configuration_type=data_output.configuration.configuration_type,
        )
        data_output = DataOutputModel(**data_output.parse_pydantic_schema())

        db.add(data_output)
        db.commit()

        RefreshInfrastructureLambda().trigger()
        return {"id": data_output.id}
