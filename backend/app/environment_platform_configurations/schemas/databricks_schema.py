from pydantic import Field

from app.shared.schema import ORMModel


class DatabricksEnvironmentPlatformConfiguration(ORMModel):
    workspace_urls: dict[str, str] = Field(
        ...,
        description=(
            "Mapping of workspace names" "to their URLs in the Databricks environment"
        ),
    )
    account_id: str = Field(
        ...,
        description=(
            "Databricks account ID associated"
            "with the environment platform configuration"
        ),
    )
    metastore_id: str = Field(
        ...,
        description=(
            "Metastore ID associated with"
            "the Databricks environment platform configuration"
        ),
    )
    credential_name: str = Field(
        ...,
        description=("Credential name used for" "accessing the Databricks environment"),
    )
