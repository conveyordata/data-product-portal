from pydantic import ConfigDict

from app.shared.schema import ORMModel


class MachineUserCreate(ORMModel):
    external_id: str
    display_name: str


class MachineUserUpdate(ORMModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    display_name: str
