from pydantic import ConfigDict

from app.shared.schema import ORMModel


class DatabricksConfig(ORMModel):
    model_config = ConfigDict(extra="forbid")
