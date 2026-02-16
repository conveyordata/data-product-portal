from enum import Enum


class DataOutputTypes(str, Enum):
    S3TechnicalAssetConfiguration = "S3TechnicalAssetConfiguration"
    DatabricksTechnicalAssetConfiguration = "DatabricksTechnicalAssetConfiguration"
    GlueTechnicalAssetConfiguration = "GlueTechnicalAssetConfiguration"
    SnowflakeTechnicalAssetConfiguration = "SnowflakeTechnicalAssetConfiguration"
    RedshiftTechnicalAssetConfiguration = "RedshiftTechnicalAssetConfiguration"
    PostgresTechnicalAssetConfiguration = "PostgresTechnicalAssetConfiguration"
