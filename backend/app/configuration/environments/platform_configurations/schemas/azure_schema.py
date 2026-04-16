from app.shared.schema import ORMModel


class AzureEnvironmentPlatformConfiguration(ORMModel):
    tenant_id: str
    subscription_id: str
    region: str
