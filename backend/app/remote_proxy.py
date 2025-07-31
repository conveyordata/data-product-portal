from __future__ import annotations

import asyncio
import webbrowser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import anyio
from fastmcp import Client, FastMCP
from fastmcp.client.auth.oauth import FileTokenStorage
from fastmcp.client.oauth_callback import (
    create_oauth_callback_server,
)
from fastmcp.utilities.logging import get_logger
from pydantic import AnyHttpUrl

from app.settings import settings
from mcp.client.auth import OAuthClientProvider
from mcp.shared.auth import (
    OAuthClientMetadata,
)

logger = get_logger(__name__)


def OAuth(
    mcp_url: str,
    scopes: str | list[str] | None = None,
    client_name: str = "FastMCP Client",
    token_storage_cache_dir: Path | None = None,
    additional_client_metadata: dict[str, Any] | None = None,
) -> OAuthClientProvider:
    """
    Create an OAuthClientProvider for an MCP server.

    This is intended to be provided to the `auth` parameter of an
    httpx.AsyncClient (or appropriate FastMCP client/transport instance)

    Args:
        mcp_url: Full URL to the MCP endpoint (e.g. "http://host/mcp/sse/")
        scopes: OAuth scopes to request. Can be a
        space-separated string or a list of strings.
        client_name: Name for this client during registration
        token_storage_cache_dir: Directory for FileTokenStorage
        additional_client_metadata: Extra fields for OAuthClientMetadata

    Returns:
        OAuthClientProvider
    """
    parsed_url = urlparse(mcp_url)
    server_base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    # Setup OAuth client
    redirect_port = 57453
    redirect_uri = f"http://localhost:{redirect_port}/callback"

    if isinstance(scopes, list):
        scopes = " ".join(scopes)

    client_metadata = OAuthClientMetadata(
        client_name=client_name,
        redirect_uris=[AnyHttpUrl(redirect_uri)],
        grant_types=["authorization_code", "refresh_token"],
        response_types=["code"],
        token_endpoint_auth_method="client_secret_post",
        scope=scopes,
        **(additional_client_metadata or {}),
    )

    # Create server-specific token storage
    storage = FileTokenStorage(
        server_url=server_base_url, cache_dir=token_storage_cache_dir
    )

    # Define OAuth handlers
    async def redirect_handler(authorization_url: str) -> None:
        """Open browser for authorization."""
        logger.info(f"OAuth authorization URL: {authorization_url}")
        webbrowser.open(authorization_url)

    async def callback_handler() -> tuple[str, str | None]:
        """Handle OAuth callback and return (auth_code, state)."""
        # Create a future to capture the OAuth response
        response_future = asyncio.get_running_loop().create_future()

        # Create server with the future
        server = create_oauth_callback_server(
            port=redirect_port,
            server_url=server_base_url,
            response_future=response_future,
        )

        # Run server until response is received with timeout logic
        async with anyio.create_task_group() as tg:
            tg.start_soon(server.serve)
            logger.info(
                f"🎧 OAuth callback server started on http://127.0.0.1:{redirect_port}"
            )

            TIMEOUT = 300.0  # 5 minute timeout
            try:
                with anyio.fail_after(TIMEOUT):
                    auth_code, state = await response_future
                    return auth_code, state
            except TimeoutError:
                raise TimeoutError(f"OAuth callback timed out after {TIMEOUT} seconds")
            finally:
                server.should_exit = True
                await asyncio.sleep(0.1)  # Allow server to shutdown gracefully
                tg.cancel_scope.cancel()

    # Create OAuth provider
    oauth_provider = OAuthClientProvider(
        server_url=server_base_url,
        client_metadata=client_metadata,
        storage=storage,
        redirect_handler=redirect_handler,
        callback_handler=callback_handler,
    )

    return oauth_provider


oauth = OAuth(mcp_url=f"{settings.HOST}/mcp/mcp/")
client = Client(f"{settings.HOST}/mcp/mcp/", auth="oauth")

server = FastMCP.as_proxy(client, name="AuthenticatedProxyDataProductPortal")

if __name__ == "__main__":
    server.run()
