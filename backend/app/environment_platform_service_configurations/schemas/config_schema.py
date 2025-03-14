from pydantic import Field

from app.shared.schema import ORMModel


class BaseEnvironmentPlatformServiceConfigurationDetail(ORMModel):
    identifier: str = Field(
        ...,
        description=(
            "Unique identifier for the"
            "environment platform service configuration detail"
        ),
    )
