from pydantic import Field

from app.shared.schema import ORMModel


class AWSEnvironmentPlatformConfiguration(ORMModel):
    account_id: str = Field(
        ...,
        description=(
            "AWS account ID associated with the environment" " platform configuration"
        ),
    )
    region: str = Field(
        ...,
        description=(
            "AWS region associated with the" "environment platform configuration"
        ),
    )
    can_read_from: list[str] = Field(
        ...,
        description=(
            "List of AWS account IDs that can read from"
            "this environment platform configuration"
        ),
    )
