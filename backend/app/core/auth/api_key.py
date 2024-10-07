import os

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel


class ApiKey(BaseModel):
    token: str


def is_valid_api_key(api_key: ApiKey) -> bool:
    backend_api_key = os.getenv("PORTAL_API_KEY")
    if not backend_api_key:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Api key access is not configured for your setup",
        )
    return backend_api_key == api_key.token


header_scheme = APIKeyHeader(name="x-key", auto_error=False)


def secured_api_key(key: str = Depends(header_scheme)) -> bool:
    if not key:
        return False
    result = is_valid_api_key(ApiKey(token=key))
    return result
