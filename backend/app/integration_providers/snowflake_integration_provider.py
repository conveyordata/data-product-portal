import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.integration_providers.integration_provider import IntegrationProvider
from app.users.schema import User


class SnowflakeIntegrationProvider(IntegrationProvider):
    def __init__(self, db: Session):
        super().__init__(db)

    def generate_url(self, id: UUID, environment: str, actor: User) -> str:
        config = json.loads(self.get_env_platform_config(id, environment, "Snowflake"))
        if "login_url" not in config:
            raise HTTPException(
                status_code=404,
                detail="login_url missing from Snowflake configuration",
            )
        return config["login_url"]
