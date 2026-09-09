from typing import Any

from pydantic import BaseModel, ConfigDict

from app.spike_plugins.interface import SpikeAssetPlugin


class S3EnvironmentConfig(BaseModel):
    """Own copy of account_id/region -- see ADR's 'Option 4' cost: this is
    duplicated in GlueEnvironmentConfig, not shared."""

    # Without this, a JSON blob shaped for a *different* plugin (e.g. one
    # missing bucket_arns) can still silently validate here if its fields
    # happen to be a subset -- exactly the ambiguous-match risk the
    # competing external ADR flagged for today's Redshift/Glue configs.
    model_config = ConfigDict(extra="forbid")

    account_id: str
    region: str
    bucket_arns: dict[str, str]  # bucket name -> ARN


class SpikeS3Plugin(SpikeAssetPlugin):
    key = "s3"
    display_name = "S3"
    icon = "s3-logo.svg"
    group = "aws"
    environment_fields = S3EnvironmentConfig

    bucket: str
    suffix: str = ""
    path: str

    def render_result(self, environment_config: dict[str, Any]) -> str:
        env = S3EnvironmentConfig.model_validate(environment_config)
        arn = env.bucket_arns.get(self.bucket)
        if arn is None:
            raise ValueError(f"No ARN configured for bucket {self.bucket!r}")
        rendered = "{arn}/{suffix}/{path}/*".format(arn=arn, **self.model_dump())
        # same trick as the real S3TechnicalAssetConfiguration.render_template:
        # strip empty path segments
        return "/".join(part for part in rendered.split("/") if part)

    def get_url(self, environment_config: dict[str, Any]) -> str:
        env = S3EnvironmentConfig.model_validate(environment_config)
        return f"https://s3.console.aws.amazon.com/s3/buckets/{self.bucket}?region={env.region}"
