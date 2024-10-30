from app.shared.schema import ORMModel


class DatabricksEnvironmentPlatformConfiguration(ORMModel):
    workspace_urls: dict[str, str]
