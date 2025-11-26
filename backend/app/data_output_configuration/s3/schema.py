from typing import Literal, Optional

from app.configuration.environments.platform_service_configurations.schemas import (
    AWSS3Config,
)
from app.data_output_configuration.base_schema import BaseDataOutputConfiguration
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.s3.model import S3DataOutput as S3DataOutputModel
from app.data_products.schema import DataProduct


class S3DataOutput(BaseDataOutputConfiguration):
    bucket: str
    suffix: str = ""
    path: str
    configuration_type: Literal[DataOutputTypes.S3DataOutput]

    class Meta:
        orm_model = S3DataOutputModel

    def validate_configuration(self, data_product: DataProduct):
        pass

    def on_create(self):
        pass

    def render_template(self, template, **context):
        return "/".join(
            [
                part
                for part in super().render_template(template, **context).split("/")
                if part
            ]
        )

    def get_configuration(self, configs: list[AWSS3Config]) -> Optional[AWSS3Config]:
        return next(
            (config for config in configs if config.identifier == self.bucket), None
        )
