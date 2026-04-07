from enum import Enum


class DataOutputTypes(str, Enum):
    S3TechnicalAssetConfiguration = "S3TechnicalAssetConfiguration"
    AzureBlobTechnicalAssetConfiguration = "AzureBlobTechnicalAssetConfiguration"
    DatabricksTechnicalAssetConfiguration = "DatabricksTechnicalAssetConfiguration"
    GlueTechnicalAssetConfiguration = "GlueTechnicalAssetConfiguration"
    SnowflakeTechnicalAssetConfiguration = "SnowflakeTechnicalAssetConfiguration"
    RedshiftTechnicalAssetConfiguration = "RedshiftTechnicalAssetConfiguration"
    PostgreSQLTechnicalAssetConfiguration = "PostgreSQLTechnicalAssetConfiguration"
    OSISemanticModelTechnicalAssetConfiguration = (
        "OSISemanticModelTechnicalAssetConfiguration"
    )
