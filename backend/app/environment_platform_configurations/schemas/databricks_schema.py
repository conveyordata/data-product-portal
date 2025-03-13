from app.shared.schema import ORMModel


class DatabricksEnvironmentPlatformConfiguration(ORMModel):
    workspace_urls: dict[str, str]
    account_id: str
    metastore_id: str
    credential_name: str
