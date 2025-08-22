from fastmcp.server.dependencies import AccessToken, get_access_token
from fastmcp.server.middleware import Middleware, MiddlewareContext

from app.core.auth.auth import get_authenticated_user
from app.core.auth.jwt import JWTToken
from app.core.logging.posthog_analytics import get_posthog_client
from app.database.database import get_db_session


class LoggingMiddleware(Middleware):
    """Middleware that logs all MCP operations."""

    def __init__(self):
        self.posthog = get_posthog_client()
        super().__init__()

    async def on_message(self, context: MiddlewareContext, call_next):
        """Called for all MCP messages."""
        entry = {
            "timestamp": context.timestamp.isoformat(),
            "source": context.source,
            "type": context.type,
            "method": context.method,
        }

        if hasattr(context.message, "__dict__"):
            try:
                entry["payload"] = context.message.__dict__
            except (TypeError, ValueError):
                entry["payload"] = "<non-serializable>"

        try:
            access_token: AccessToken = get_access_token()
            user_id = get_authenticated_user(
                token=JWTToken(sub="", token=f"Bearer {access_token.token}"),
                db=next(get_db_session()),
            ).id
        except Exception:
            user_id = None

        if self.posthog:
            # Log to PostHog
            self.posthog.capture(
                distinct_id=user_id,
                event="MCP Method Call API",
                properties=entry,
            )
        result = await call_next(context)
        return result
