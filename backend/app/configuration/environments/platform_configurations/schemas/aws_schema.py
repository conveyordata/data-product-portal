from app.shared.schema import ORMModel


class AWSEnvironmentPlatformConfiguration(ORMModel):
    account_id: str
    region: str
    can_read_from: list[str]
