"""Shared MCP infrastructure: database sessions and authentication.

Kept in a separate module so both core portal tools and plugin tools can import
these utilities without creating circular dependencies.
"""

from typing import Any, Optional

import jwt as pyjwt
from fastmcp.dependencies import Depends
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from fastmcp.server.dependencies import get_access_token
from sqlalchemy import select as sa_select
from sqlalchemy.orm import Session, configure_mappers

from app.core.auth.auth import get_authenticated_user
from app.core.auth.jwt import get_oidc
from app.core.authz import Action, Authorization
from app.core.logging import logger
from app.data_products.model import DataProduct as DataProductModel
from app.database.database import db_session
from app.settings import settings
from app.users.model import User
from app.users.model import User as UserModel


def initialize_models() -> None:
    """Initialize all SQLAlchemy models and resolve relationships."""
    try:
        configure_mappers()
    except Exception as e:
        logger.warn(f"Warning during model initialization: {e}")


class PortalOIDCProxy(OIDCProxy):
    async def _extract_upstream_claims(
        self, idp_tokens: dict[str, Any]
    ) -> dict[str, Any] | None:
        for key in ("id_token", "access_token"):
            raw = idp_tokens.get(key, "")
            if not raw:
                continue
            try:
                claims = pyjwt.decode(raw, options={"verify_signature": False})
                extracted = {
                    k: claims[k]
                    for k in ("sub", "email", "name", "family_name")
                    if k in claims
                }
                if extracted.get("sub"):
                    logger.debug(
                        f"[MCP] Extracted upstream claims from {key}: "
                        f"sub={extracted.get('sub')!r}, email={extracted.get('email')!r}"
                    )
                    return extracted
            except Exception as exc:
                logger.error(f"[MCP] Could not decode {key} as JWT: {exc}")
        logger.warning(
            "[MCP] _extract_upstream_claims: no usable token found in IDP response"
        )
        return None


def get_auth_provider() -> Optional[PortalOIDCProxy]:
    if settings.OIDC_ENABLED:
        from key_value.aio.stores.postgresql import PostgreSQLStore

        from app.database.database import get_url

        oidc = get_oidc()
        client_storage = PostgreSQLStore(url=get_url())
        return PortalOIDCProxy(
            config_url=f"{oidc.authority}/.well-known/openid-configuration",
            client_id=oidc.client_id,
            client_secret=oidc.client_secret,
            base_url=f"{(settings.MCP_BASE_URL or settings.HOST).rstrip('/')}/mcp",
            require_authorization_consent="external",
            allowed_client_redirect_uris=settings.MCP_AUTH_REDIRECT_URIS,
            client_storage=client_storage,
        )
    logger.debug("[MCP] OIDC disabled — MCP server will run without authentication")
    return None


def get_mcp_authenticated_user(db: Session = Depends(db_session)) -> UserModel:
    """Get the authenticated portal user from the current MCP request context.

    When OIDC is enabled the FastMCP access token carries upstream identity claims
    extracted from the upstream OIDC id_token. These claims are used for a direct
    DB lookup — no extra userinfo round-trip.

    When OIDC is disabled the default portal user is returned.
    """
    if not settings.OIDC_ENABLED:
        from app.core.auth.auth import generate_default_jwt_token

        logger.debug("[MCP] OIDC disabled — resolving default user")
        return get_authenticated_user(token=generate_default_jwt_token(), db=db)

    access_token = get_access_token()
    if access_token is None:
        logger.warning("[MCP] get_mcp_authenticated_user: no access token in context")
        raise ValueError("No access token found in MCP context")

    logger.debug(
        f"[MCP] Access token present: client_id={access_token.client_id!r}, "
        f"scopes={access_token.scopes!r}, has_claims={bool(access_token.claims)}"
    )

    upstream_claims = (
        access_token.claims.get("upstream_claims") if access_token.claims else None
    )
    if not upstream_claims:
        raise ValueError("No upstream_claims found in access token")

    sub = upstream_claims.get("sub")
    if not sub:
        raise ValueError(f"upstream_claims missing 'sub' claim: {upstream_claims!r}")
    logger.debug(f"[MCP] Resolving user from upstream_claims: sub={sub!r}")

    user_model = db.scalar(sa_select(UserModel).where(UserModel.external_id == sub))
    if not user_model:
        logger.error(f"[MCP] Authenticated user not found in DB: sub={sub!r}")
        raise ValueError(f"Authenticated user not found: sub={sub!r}")

    logger.debug(f"[MCP] Resolved user from upstream_claims: sub={sub!r}")
    return user_model


def get_user_db_session(user: User = Depends(get_mcp_authenticated_user)):
    with db_session() as db:
        db.info["current_user_id"] = user.id
        try:
            yield db
        finally:
            db.info.pop("current_user_id", None)


def authorize_data_product_read_integrations(
    data_product_namespace: str,
    authorized_user=Depends(get_mcp_authenticated_user),
    db: Session = Depends(get_user_db_session),
) -> None:
    """Verify authenticated user has READ_INTEGRATIONS access to the data product.

    Raises an error if not authorized.
    """
    data_product = db.scalar(
        sa_select(DataProductModel).where(
            DataProductModel.namespace == data_product_namespace
        )
    )
    if not data_product:
        raise ValueError(f"Data product '{data_product_namespace}' not found")

    domain_id = data_product.domain_id
    dom = str(domain_id) if domain_id else "*"
    obj = str(data_product.id)
    sub = str(authorized_user.id)

    if not Authorization().has_access(
        sub=sub, dom=dom, obj=obj, act=Action.DATA_PRODUCT__READ_INTEGRATIONS
    ):
        raise PermissionError(
            f"User {authorized_user.id} does not have permission to read integrations "
            f"for data product {data_product_namespace}"
        )
