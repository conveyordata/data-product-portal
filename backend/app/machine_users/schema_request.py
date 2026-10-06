from pydantic import ConfigDict

from app.shared.schema import NonEmptyStr, ORMModel


class MachineUserCreate(ORMModel):
    external_id: NonEmptyStr
    display_name: NonEmptyStr


class MachineUserUpdate(ORMModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    display_name: NonEmptyStr
