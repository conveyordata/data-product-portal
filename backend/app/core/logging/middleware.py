import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import logger


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.time()
        status_code = 500
        path = scope.get("path", "")
        method = scope.get("method", "")

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        await self.app(scope, receive, send_wrapper)

        if path != "/":
            logger.info(
                {
                    "url": path,
                    "method": method,
                    "status": status_code,
                    "process_time": time.time() - start,
                }
            )
