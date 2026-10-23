from pydantic import BaseModel, ConfigDict


class IdentifiedSettings(BaseModel):
    identifier: str


class S3BucketSettings(IdentifiedSettings):
    bucket_name: str
    bucket_arn: str
    kms_key_arn: str
    is_default: bool


class GlueDatabaseSettings(IdentifiedSettings):
    database_name: str
    bucket_identifier: str
    s3_path: str
    athena_workgroup_template: str = ""


class RedshiftDatabaseSettings(IdentifiedSettings):
    database_name: str
    bucket_identifier: str
    s3_path: str


class PostgreSQLDatabaseSettings(IdentifiedSettings):
    host: str
    port: str
    admin_user: str
    admin_pwd: str


class DatabricksCatalogSettings(IdentifiedSettings):
    model_config = ConfigDict(extra="forbid")


class SnowflakeDatabaseSettings(IdentifiedSettings):
    database_name: str


class AzureBlobSettings(IdentifiedSettings):
    storage_account_names: dict[str, str]


class AWSSettings(BaseModel):
    account_id: str = ""
    region: str = ""
    can_read_from: list[str] = []
    s3: list[S3BucketSettings] = []
    glue: list[GlueDatabaseSettings] = []
    redshift: list[RedshiftDatabaseSettings] = []


class AzureSettings(BaseModel):
    tenant_id: str = ""
    subscription_id: str = ""
    region: str = ""
    azureblob: list[AzureBlobSettings] = []


class DatabricksSettings(BaseModel):
    workspace_urls: dict[str, str] = {}
    account_id: str = ""
    metastore_id: str = ""
    credential_name: str = ""
    databricks: list[DatabricksCatalogSettings] = []


class SnowflakeSettings(BaseModel):
    login_url: str = ""
    snowflake: list[SnowflakeDatabaseSettings] = []


class PostgreSQLSettings(BaseModel):
    postgresql: list[PostgreSQLDatabaseSettings] = []
