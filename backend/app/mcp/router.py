import time

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.auth.jwt import get_oidc
from app.core.logging import logger
from app.settings import settings

router = APIRouter(prefix="", tags=["mcp"])


@router.get("/.well-known/oauth-authorization-server")
def oauth_metadata() -> JSONResponse:
    """OAuth 2.1 Authorization Server Metadata."""
    return JSONResponse(
        {
            "issuer": get_oidc().authority,
            "authorization_endpoint": get_oidc().authorization_endpoint,
            "token_endpoint": get_oidc().token_endpoint,
            "jwks_uri": get_oidc().jwks_uri,
            "registration_endpoint": f"{settings.HOST.rstrip('/')}/api/register",
            "response_types_supported": ["code"],
            "code_challenge_methods_supported": ["S256"],
            "token_endpoint_auth_methods_supported": ["client_secret_post"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
        }
    )


# OpenID Connect Discovery endpoint
@router.get("/.well-known/openid-configuration")
async def openid_config():
    """OpenID Connect Discovery endpoint."""
    # In a real implementation, you might proxy to an actual OIDC provider
    return JSONResponse(
        {
            "issuer": get_oidc().authority,
            "authorization_endpoint": get_oidc().authorization_endpoint,
            "token_endpoint": get_oidc().token_endpoint,
            "jwks_uri": get_oidc().jwks_uri,
            "response_types_supported": ["code"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }
    )


# OAuth Protected Resource Metadata
@router.get("/.well-known/oauth-protected-resource")
def oauth_protected_resource():
    """OAuth 2.1 Protected Resource Metadata."""
    BASE_URL = f"{settings.HOST.rstrip('/')}/"
    return JSONResponse(
        {
            "resource": BASE_URL,
            "authorization_servers": [BASE_URL],
            "jwks_uri": get_oidc().jwks_uri,
            "bearer_methods_supported": ["header"],
            "resource_documentation": f"{BASE_URL}docs",
        }
    )


# Dynamic Client Registration endpoint
@router.post("/api/register")
async def register(request: Request):
    """OAuth 2.1 Dynamic Client Registration endpoint."""
    # Redact sensitive headers before logging
    headers = dict(request.headers)
    for sensitive_header in ["authorization", "cookie", "set-cookie"]:
        if sensitive_header in headers:
            headers[sensitive_header] = "[REDACTED]"
    logger.info(f"/register headers: {headers}")

    # Do not log raw body to avoid leaking sensitive information

    try:
        data = await request.json()
        # Do not print or log raw data directly, as it may contain sensitive information
        logger.info("/register parsed data received (fields redacted for privacy)")
    except Exception as e:
        logger.error(f"Failed to parse JSON body: {e}")
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    # Generate client credentials
    client_id = get_oidc().client_id
    client_secret = get_oidc().client_secret
    now = int(time.time())

    # Build the response according to OAuth 2.0 Dynamic Client Registration spec
    response_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "client_id_issued_at": now,
        "client_secret_expires_at": 0,  # 0 means no expiration
        "redirect_uris": [settings.HOST.rstrip("/")],
        "token_endpoint_auth_method": data.get(
            "token_endpoint_auth_method", "client_secret_post"
        ),
        "grant_types": data.get("grant_types", ["authorization_code"]),
        "response_types": data.get("response_types", ["code"]),
        "client_name": data.get("client_name", ""),
        "scope": data.get("scope", ""),
    }
    return JSONResponse(response_data, status_code=201)
