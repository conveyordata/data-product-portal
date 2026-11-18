import json
from contextlib import suppress
from typing import Any, Optional
from uuid import UUID

from fastmcp.server.middleware import Middleware, MiddlewareContext

from app.core.logging.posthog_analytics import PosthogAnalyticsClient
from app.mcp.deps import MCP_USER_ID_STATE_KEY


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
        try:
            return await call_next(context)
        finally:
            self.posthog.capture(
                distinct_id=await self._get_user_id(context) or "unknown",
                event="MCP Method Call API",
                properties=entry,
                timestamp=context.timestamp,
            )

    @staticmethod
    async def _get_user_id(context: MiddlewareContext) -> Optional[UUID]:
        with suppress(Exception):
            if (ctx := context.fastmcp_context) is not None:
                return await ctx.get_state(MCP_USER_ID_STATE_KEY)
        return None

    @staticmethod
    def _extract_payload(message: Any) -> str:
        """Return JSON-encoded payload or placeholder string."""
        try:
            return json.dumps(message, default=lambda o: vars(o), ensure_ascii=False)
        except Exception:
            return "<non-serializable>"
