from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.users.schema import User


def get_azure_plugin_url(
    cls: type[object],
    id: UUID,
    db: Session,
    actor: User,
    environment: Optional[str] = None,
) -> str:
    return "https://portal.azure.com/"
