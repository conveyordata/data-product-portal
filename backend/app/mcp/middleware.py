import asyncio
import json
from typing import Any, Optional

from fastmcp.server.middleware import Middleware, MiddlewareContext

from app.core.logging.posthog_analytics import PosthogAnalyticsClient
from app.database.database import db_session
from app.mcp.deps import get_mcp_authenticated_user


class LoggingMiddleware(Middleware):
    """Middleware that logs all MCP operations to PostHog analytics."""

    def __init__(self) -> None:
        super().__init__()
        self.posthog = PosthogAnalyticsClient()

    async def on_message(self, context: MiddlewareContext, call_next) -> Any:
        """Called for all MCP messages."""
        entry = {
            "timestamp": context.timestamp.isoformat(),
            "source": context.source,
            "type": context.type,
            "method": context.method,
            "payload": self._extract_payload(context.message),
        }
        user_id = await self._get_user_id()
        self.posthog.capture(
            distinct_id=user_id or "unknown",
            event="MCP Method Call API",
            properties=entry,
        )

        return await call_next(context)

    def _extract_payload(self, message: Any) -> str:
        """Return JSON-encoded payload or placeholder string."""
        try:
            return json.dumps(message, default=lambda o: vars(o), ensure_ascii=False)
        except Exception:
            return "<non-serializable>"

    async def _get_user_id(self) -> Optional[str]:
        """Get the authenticated user ID, returning None if not available."""
        try:
            return await asyncio.to_thread(self._lookup_user_id)
        except Exception:
            return None

    @staticmethod
    def _lookup_user_id() -> str:
        with db_session() as db:
            return str(get_mcp_authenticated_user(db).id)
