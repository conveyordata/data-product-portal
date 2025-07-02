import json
from urllib import parse
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.datasets.model import Dataset
from app.integration_providers.integration_provider import IntegrationProvider
from app.users.schema import User


class SodaIntegrationProvider(IntegrationProvider):
    def __init__(self, db: Session):
        super().__init__(db)

    def generate_url(self, id: UUID, environment: str, actor: User) -> str:
        config = json.loads(self.get_env_platform_config(id, environment, "Soda"))
        dataset = self.db.get(Dataset, id)
        if "soda_organization" not in config:
            raise HTTPException(
                status_code=404,
                detail="soda_organization missing from Soda configuration",
            )

        filter_key = config.get("soda_filter_key", "dataset")

        returnUrl = (
            "https://cloud.soda.io/datasets/"
            f"overview?filters=(f{filter_key}!f{dataset.name})_"
        )
        return (
            "https://cloud.soda.io/sso/signin/"
            f'{config.get("soda_organization")}/?'
            f"returnUrl={parse.quote_plus(returnUrl)}"
        )
