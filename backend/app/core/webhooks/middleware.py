import asyncio
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Any

from fastapi import FastAPI
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.context import close_event_context, open_event_context, pop_events
from app.core.logging import logger
from app.core.webhooks.events import V2Event
from app.core.webhooks.v2 import emit_all_events
from app.settings import settings

_EVENT_QUEUE_MAXSIZE = 1000
_INFLIGHT_DRAIN_TIMEOUT_SECONDS = 10.0
_QUEUE_DRAIN_TIMEOUT_SECONDS = 10.0
_DISPATCHER_STATE_KEY = "webhook_v2_dispatcher"


class EventDispatcher:
    """Dispatches webhook v2 events to a background worker.

    Requests hand off their events to a queue so the response is not delayed by
    the webhook call. Shutdown waits for in-flight requests to submit their
    events and for the queue to drain, both under a bounded timeout.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[list[V2Event]] = asyncio.Queue(
            maxsize=_EVENT_QUEUE_MAXSIZE
        )
        self._inflight_requests = 0
        self._idle = asyncio.Event()
        self._idle.set()
        self._task = asyncio.create_task(self._worker(), name="webhook_v2_dispatcher")
        self._task.add_done_callback(_log_task_result)
        self._loop = asyncio.get_running_loop()

    def is_running(self) -> bool:
        """Whether the worker is still usable from the running event loop.

        The queue and its worker are bound to the loop they were created on, so
        a dispatcher outlives its loop only as an unusable leftover.
        """
        with suppress(RuntimeError):
            return not self._task.done() and self._loop is asyncio.get_running_loop()
        return False

    async def _worker(self) -> None:
        while True:
            try:
                events = await self._queue.get()
            except asyncio.QueueShutDown:
                return
            try:
                await emit_all_events(events)
            except Exception:
                logger.exception("Failed to dispatch queued webhook v2 events")
            finally:
                self._queue.task_done()

    def request_started(self) -> None:
        self._inflight_requests += 1
        self._idle.clear()

    def request_finished(self) -> None:
        self._inflight_requests = max(self._inflight_requests - 1, 0)
        if self._inflight_requests == 0:
            self._idle.set()

    def submit(self, events: list[V2Event]) -> None:
        try:
            self._queue.put_nowait(events)
        except asyncio.QueueFull:
            logger.warning(
                "Webhook v2 event queue is full, dropping %s events", len(events)
            )
        except asyncio.QueueShutDown:
            logger.warning(
                "Webhook v2 event queue is shut down, dropping %s events", len(events)
            )

    async def stop(self) -> None:
        # The queue stays open here so in-flight requests can still submit.
        await self._wait_for(
            self._idle.wait(),
            _INFLIGHT_DRAIN_TIMEOUT_SECONDS,
            "Timed out waiting for %s in-flight request(s) before webhook v2 shutdown",
            lambda: self._inflight_requests,
        )

        self._queue.shutdown(immediate=False)
        await self._wait_for(
            self._queue.join(),
            _QUEUE_DRAIN_TIMEOUT_SECONDS,
            "Timed out draining webhook v2 event queue, dropping %s queued batch(es)",
            self._queue.qsize,
        )

        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task

    @staticmethod
    async def _wait_for(
        awaitable: Awaitable[Any],
        timeout: float,
        message: str,
        remaining: Callable[[], int],
    ) -> None:
        try:
            await asyncio.wait_for(awaitable, timeout=timeout)
        except TimeoutError:
            logger.warning(message, remaining())


def _log_task_result(task: asyncio.Task[None]) -> None:
    if task.cancelled():
        return
    if exc := task.exception():
        logger.exception("Background task '%s' failed", task.get_name(), exc_info=exc)


def start_event_dispatcher(app: FastAPI) -> EventDispatcher:
    """Start a dispatcher, replacing any dispatcher left by a previous run.

    The FastAPI application object is a module level singleton, so its state
    survives a lifespan cycle and has to be replaced rather than reused.
    """
    dispatcher = EventDispatcher()
    setattr(app.state, _DISPATCHER_STATE_KEY, dispatcher)
    return dispatcher


async def stop_event_dispatcher(app: FastAPI) -> None:
    dispatcher = getattr(app.state, _DISPATCHER_STATE_KEY, None)
    if dispatcher is not None:
        await dispatcher.stop()


def _get_event_dispatcher(app: FastAPI) -> EventDispatcher:
    dispatcher = getattr(app.state, _DISPATCHER_STATE_KEY, None)
    if dispatcher is None or not dispatcher.is_running():
        dispatcher = start_event_dispatcher(app)
    return dispatcher


class DispatchQueuedEventsMiddleware:
    def __init__(self, app: ASGIApp, fastapi_app: FastAPI) -> None:
        if not isinstance(fastapi_app, FastAPI):
            raise TypeError(
                "DispatchQueuedEventsMiddleware requires the FastAPI application, "
                f"got {type(fastapi_app).__name__}"
            )
        self.app = app
        self.fastapi_app = fastapi_app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Held for the whole request so a restart cannot split the in-flight
        # bookkeeping across two dispatchers.
        dispatcher = _get_event_dispatcher(self.fastapi_app)
        dispatcher.request_started()

        token = open_event_context()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        try:
            try:
                await self.app(scope, receive, send_wrapper)
            finally:
                events = pop_events()
                close_event_context(token)
                # Submit before finishing so a concurrent shutdown never
                # sees zero in-flight requests while events are pending.
                self._submit(dispatcher, events, status_code)
        finally:
            dispatcher.request_finished()

    @staticmethod
    def _submit(
        dispatcher: EventDispatcher, events: list[V2Event], status_code: int
    ) -> None:
        if not events or not settings.WEBHOOK_V2_URL:
            return
        if status_code >= 400:
            logger.debug(
                "Request failed with status %s, dropping %s webhook v2 events",
                status_code,
                len(events),
            )
            return
        dispatcher.submit(events)
