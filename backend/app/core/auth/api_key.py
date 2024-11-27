import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.data_products.model import DataProduct as DataProductModel
from app.data_products.schema_base_get import BaseDataProductGet
from app.database.database import get_db_session


class ApiKey(BaseModel):
    token: str
    project: Optional[BaseDataProductGet] = None


def is_valid_api_key(api_key: ApiKey, db: Session) -> Optional[ApiKey]:
    # Project based access
    project_based_access = (
        db.query(DataProductModel)
        .filter(DataProductModel.api_key == api_key.token)
        .first()
    )
    if project_based_access:
        return ApiKey(token=api_key.token, project=project_based_access)

    # Full backend API Keys
    backend_api_key = os.getenv("PORTAL_API_KEY")
    if not backend_api_key:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Api key access is not configured for your setup",
        )
    if backend_api_key == api_key.token:
        return api_key
    return None


header_scheme = APIKeyHeader(name="x-key", auto_error=False)


def secured_api_key(
    key: str = Depends(header_scheme), db: Session = Depends(get_db_session)
) -> Optional[ApiKey]:
    if not key:
        return None
    result = is_valid_api_key(ApiKey(token=key), db)
    return result
