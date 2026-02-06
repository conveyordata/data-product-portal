from sqlalchemy import String

from app.data_output_configuration.base_model import BaseTechnicalAssetConfiguration


class PostgresTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    database: String
    schema: String
    table: String
    bucket_identifier: String
    database_path: String
    table_path: String
    access_granularity: String

    __mapper_args__ = {
        "polymorphic_identity": "PostgresTechnicalAssetConfiguration",
    }
