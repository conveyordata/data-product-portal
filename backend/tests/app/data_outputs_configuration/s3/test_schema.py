import pytest

from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.s3.schema import S3TechnicalAssetConfiguration


def make_s3_config(
    suffix: str,
    path: str,
    bucket: str,
) -> S3TechnicalAssetConfiguration:
    return S3TechnicalAssetConfiguration(
        bucket=bucket,
        path=path,
        suffix=suffix,
        configuration_type=DataOutputTypes.S3TechnicalAssetConfiguration,
    )


class TestRenderTemplate:
    def test_resolves_s3_path_for_matching_bucket(self):
        config = make_s3_config(suffix="customer360", path="output", bucket="datalake")
        result = config.render_template(
            template="{bucket_arn}/{suffix}/{path}/*",
            bucket_name="datalake",
            bucket_arn="datalakeartifacts",
        )
        assert result == "datalakeartifacts/customer360/output/*"

    def test_fails_bucket_lookup(self):
        config = make_s3_config(suffix="customer360", path="output", bucket="datalake")
        with pytest.raises(KeyError):
            config.render_template(
                template="{bucket_arn}/{suffix}/{path}/*",
            )
