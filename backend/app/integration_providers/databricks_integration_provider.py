import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data_products.model import DataProduct as DataProductModel
from app.integration_providers.integration_provider import IntegrationProvider
from app.users.schema import User


class DatabricksIntegrationProvider(IntegrationProvider):
    def __init__(self, db: Session):
        super().__init__(db)

    def generate_url(self, id: UUID, environment: str, actor: User) -> str:
        config = json.loads(self.get_env_platform_config(id, environment, "Databricks"))
        data_product = self.db.get(DataProductModel, id)
        domain_id = str(data_product.domain_id)
        if domain_id not in config["workspace_urls"]:
            raise HTTPException(
                status_code=404,
                detail=f"Workspace not configured \
                for domain {data_product.domain.name}",
            )
        return config["workspace_urls"][domain_id]
