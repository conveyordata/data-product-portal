from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.spike_plugins.interface import SpikeAssetPlugin


class GlueEnvironmentConfig(BaseModel):
    """Own copy of account_id/region -- duplicated with S3EnvironmentConfig,
    not shared. This is the cost ADR-0024's chosen Option 4 accepts."""

    model_config = ConfigDict(extra="forbid")

    account_id: str
    region: str


class SpikeGluePlugin(SpikeAssetPlugin):
    key = "glue"
    display_name = "Glue"
    icon = "glue-logo.svg"
    group = "aws"
    environment_fields = GlueEnvironmentConfig

    database: str
    database_suffix: str = ""
    table: str = "*"
    access_granularity: Literal["schema", "table"] = "schema"

    def validate_configuration(self, *, namespace: str | None = None) -> None:
        # same rule as the real GlueTechnicalAssetConfiguration
        if namespace and not self.database.startswith(namespace):
            raise ValueError(
                f"database {self.database!r} must start with namespace {namespace!r}"
            )

    def render_result(self, environment_config: dict[str, Any]) -> str:
        rendered = "{database}.{table}".format(**self.model_dump())
        # same trick as the real GlueTechnicalAssetConfiguration.render_template
        return ".".join(part.rstrip("_") for part in rendered.split("."))

    def get_url(self, environment_config: dict[str, Any]) -> str:
        env = GlueEnvironmentConfig.model_validate(environment_config)
        return (
            f"https://console.aws.amazon.com/glue/home?region={env.region}"
            f"#table:catalog={env.account_id};name={self.table}"
        )
