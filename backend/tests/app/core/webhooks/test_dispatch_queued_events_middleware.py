"""Tests for the webhook v2 event dispatch middleware."""

import asyncio
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from fastapi import FastAPI, HTTPException

from app.core.context import queue_event
from app.core.webhooks import middleware as mw
from app.core.webhooks.events import V2Event
from app.core.webhooks.middleware import (
    DispatchQueuedEventsMiddleware,
    EventDispatcher,
    start_event_dispatcher,
    stop_event_dispatcher,
)
from tests.conftest import webhook_v2_config


class _SampleEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "dispatch.sample.event"

    value: str = "sample"


def build_app() -> FastAPI:
    """An app wired like main.py, with routes covering the relevant outcomes."""
    app = FastAPI()
    app.add_middleware(DispatchQueuedEventsMiddleware, fastapi_app=app)

    @app.get("/ok")
    async def ok() -> dict[str, bool]:
        queue_event(_SampleEvent())
        return {"ok": True}

    @app.get("/no-events")
    async def no_events() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/client-error")
    async def client_error() -> None:
        queue_event(_SampleEvent())
        raise HTTPException(status_code=400)

    @app.get("/crash")
    async def crash() -> None:
        queue_event(_SampleEvent())
        raise ValueError("boom")

    return app


def client(app: FastAPI) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


def capture_emitted(emitted: list[V2Event]) -> Any:
    async def _emit(events: list[V2Event]) -> None:
        emitted.extend(events)

    return patch.object(mw, "emit_all_events", _emit)


class TestEventDispatching:
    @pytest.mark.asyncio
    async def test_dispatches_events_of_successful_request(self):
        app = build_app()
        start_event_dispatcher(app)
        emitted: list[V2Event] = []

        with webhook_v2_config(), capture_emitted(emitted):
            async with client(app) as http:
                response = await http.get("/ok")
            await stop_event_dispatcher(app)

        assert response.status_code == 200
        assert [type(event) for event in emitted] == [_SampleEvent]

    @pytest.mark.asyncio
    async def test_does_not_dispatch_when_url_not_configured(self):
        app = build_app()
        start_event_dispatcher(app)
        emitted: list[V2Event] = []

        with webhook_v2_config(url=None), capture_emitted(emitted):
            async with client(app) as http:
                await http.get("/ok")
            await stop_event_dispatcher(app)

        assert emitted == []

    @pytest.mark.asyncio
    async def test_does_not_dispatch_events_of_failed_request(self):
        app = build_app()
        start_event_dispatcher(app)
        emitted: list[V2Event] = []

        with webhook_v2_config(), capture_emitted(emitted):
            async with client(app) as http:
                response = await http.get("/client-error")
            await stop_event_dispatcher(app)

        assert response.status_code == 400
        assert emitted == []

    @pytest.mark.asyncio
    async def test_does_not_dispatch_when_handler_raises(self):
        app = build_app()
        start_event_dispatcher(app)
        emitted: list[V2Event] = []

        with webhook_v2_config(), capture_emitted(emitted):
            async with client(app) as http:
                response = await http.get("/crash")
            await stop_event_dispatcher(app)

        assert response.status_code == 500
        assert emitted == []

    @pytest.mark.asyncio
    async def test_request_succeeds_when_dispatching_fails(self):
        """A broken webhook target must not surface in the response."""
        app = build_app()
        start_event_dispatcher(app)

        async def _boom(events: list[V2Event]) -> None:
            raise RuntimeError("webhook exploded")

        with webhook_v2_config(), patch.object(mw, "emit_all_events", _boom):
            async with client(app) as http:
                response = await http.get("/ok")
            await stop_event_dispatcher(app)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_drops_events_when_queue_is_full(self):
        """A full queue drops events instead of failing the request."""
        app = build_app()
        dispatcher = start_event_dispatcher(app)
        dispatching = asyncio.Event()
        blocked = asyncio.Event()

        async def _block(events: list[V2Event]) -> None:
            dispatching.set()
            await blocked.wait()

        with webhook_v2_config(), patch.object(mw, "emit_all_events", _block):
            # Occupy the worker so that it stops draining the queue.
            dispatcher._queue.put_nowait([_SampleEvent()])
            await asyncio.wait_for(dispatching.wait(), timeout=5)
            while not dispatcher._queue.full():
                dispatcher._queue.put_nowait([_SampleEvent()])

            with patch.object(mw.logger, "warning") as warning:
                async with client(app) as http:
                    response = await http.get("/ok")

            blocked.set()
            with patch.object(mw, "_QUEUE_DRAIN_TIMEOUT_SECONDS", 5):
                await stop_event_dispatcher(app)

        assert response.status_code == 200
        assert "queue is full" in warning.call_args.args[0]

    @pytest.mark.asyncio
    async def test_submitting_to_stopped_dispatcher_drops_events(self):
        app = build_app()
        dispatcher = start_event_dispatcher(app)
        await stop_event_dispatcher(app)

        with patch.object(mw.logger, "warning") as warning:
            dispatcher.submit([_SampleEvent()])

        assert "shut down" in warning.call_args.args[0]


class TestInflightTracking:
    @pytest.mark.asyncio
    async def test_inflight_returns_to_zero_after_request(self):
        app = build_app()
        dispatcher = start_event_dispatcher(app)

        with webhook_v2_config(), capture_emitted([]):
            async with client(app) as http:
                await http.get("/ok")
                await http.get("/crash")
            await stop_event_dispatcher(app)

        assert dispatcher._inflight_requests == 0

    @pytest.mark.asyncio
    async def test_shutdown_dispatches_events_of_inflight_request(self):
        """Events submitted while shutdown is draining must still be sent."""
        app = build_app()
        start_event_dispatcher(app)
        emitted: list[V2Event] = []
        release = asyncio.Event()

        @app.get("/blocked")
        async def blocked() -> dict[str, bool]:
            await release.wait()
            queue_event(_SampleEvent())
            return {"ok": True}

        app.middleware_stack = None

        with webhook_v2_config(), capture_emitted(emitted):
            async with client(app) as http:
                request = asyncio.create_task(http.get("/blocked"))
                await asyncio.sleep(0)
                shutdown = asyncio.create_task(stop_event_dispatcher(app))
                await asyncio.sleep(0)

                release.set()
                await request
                await shutdown

        assert len(emitted) == 1

    @pytest.mark.asyncio
    async def test_shutdown_gives_up_on_stuck_request(self):
        """A never-finishing request must not block shutdown forever."""
        app = build_app()
        start_event_dispatcher(app)

        @app.get("/hangs")
        async def hangs() -> None:
            await asyncio.sleep(60)

        app.middleware_stack = None

        with (
            webhook_v2_config(),
            patch.object(mw, "_INFLIGHT_DRAIN_TIMEOUT_SECONDS", 0.05),
        ):
            async with client(app) as http:
                request = asyncio.create_task(http.get("/hangs"))
                await asyncio.sleep(0)

                await asyncio.wait_for(stop_event_dispatcher(app), timeout=5)

                request.cancel()


class TestDispatcherLifecycle:
    @pytest.mark.asyncio
    async def test_shutdown_gives_up_on_slow_dispatching(self):
        app = build_app()
        dispatcher = start_event_dispatcher(app)
        for _ in range(3):
            dispatcher._queue.put_nowait([_SampleEvent()])

        async def _slow(events: list[V2Event]) -> None:
            await asyncio.sleep(60)

        with (
            patch.object(mw, "emit_all_events", _slow),
            patch.object(mw, "_QUEUE_DRAIN_TIMEOUT_SECONDS", 0.05),
        ):
            await asyncio.wait_for(stop_event_dispatcher(app), timeout=5)

        assert dispatcher._task.done()

    @pytest.mark.asyncio
    async def test_stop_is_a_noop_without_dispatcher(self):
        await stop_event_dispatcher(FastAPI())

    @pytest.mark.asyncio
    async def test_restart_dispatches_events_again(self):
        """The app object is a singleton, so a second lifespan must work."""
        app = build_app()
        start_event_dispatcher(app)
        await stop_event_dispatcher(app)
        start_event_dispatcher(app)
        emitted: list[V2Event] = []

        with webhook_v2_config(), capture_emitted(emitted):
            async with client(app) as http:
                await http.get("/ok")
            await stop_event_dispatcher(app)

        assert len(emitted) == 1

    @pytest.mark.asyncio
    async def test_dispatcher_is_replaced_when_bound_to_another_loop(self):
        """Each TestClient runs its own loop; a dispatcher cannot cross loops."""
        app = build_app()
        emitted: list[V2Event] = []

        with _dispatcher_on_another_loop() as stale:
            setattr(app.state, "webhook_v2_dispatcher", stale)
            assert not stale.is_running()

            with webhook_v2_config(), capture_emitted(emitted):
                async with client(app) as http:
                    await http.get("/ok")
                await stop_event_dispatcher(app)

            assert getattr(app.state, "webhook_v2_dispatcher") is not stale
            assert stale._queue.empty()

        assert len(emitted) == 1

    @pytest.mark.asyncio
    async def test_dispatcher_is_replaced_when_worker_stopped(self):
        app = build_app()
        dispatcher = start_event_dispatcher(app)
        await stop_event_dispatcher(app)
        emitted: list[V2Event] = []

        assert not dispatcher.is_running()

        with webhook_v2_config(), capture_emitted(emitted):
            async with client(app) as http:
                await http.get("/ok")
            await stop_event_dispatcher(app)

        assert getattr(app.state, "webhook_v2_dispatcher") is not dispatcher
        assert len(emitted) == 1

    @pytest.mark.asyncio
    async def test_running_dispatcher_is_reused(self):
        app = build_app()
        dispatcher = start_event_dispatcher(app)

        with webhook_v2_config(), capture_emitted([]):
            async with client(app) as http:
                await http.get("/ok")
                await http.get("/ok")

            assert getattr(app.state, "webhook_v2_dispatcher") is dispatcher
            await stop_event_dispatcher(app)


@contextmanager
def _dispatcher_on_another_loop() -> Iterator[EventDispatcher]:
    """A dispatcher owned by a second, still running event loop."""
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    try:
        dispatcher = asyncio.run_coroutine_threadsafe(_make_dispatcher(), loop).result(
            timeout=5
        )
        yield dispatcher
    finally:
        loop.call_soon_threadsafe(dispatcher._task.cancel)
        loop.call_soon_threadsafe(loop.stop)
        thread.join(timeout=5)
        loop.close()


async def _make_dispatcher() -> EventDispatcher:
    return EventDispatcher()


class TestMiddlewareConstruction:
    def test_requires_the_fastapi_application(self):
        async def inner(scope, receive, send) -> None: ...

        with pytest.raises(TypeError, match="requires the FastAPI application"):
            DispatchQueuedEventsMiddleware(inner, fastapi_app=inner)

    @pytest.mark.asyncio
    async def test_passes_through_non_http_scopes(self):
        """Non-http scopes bypass event handling entirely."""
        received: list[str] = []

        async def inner(scope, receive, send) -> None:
            received.append(scope["type"])

        app = FastAPI()
        middleware = DispatchQueuedEventsMiddleware(inner, fastapi_app=app)
        await middleware({"type": "websocket"}, None, None)

        assert received == ["websocket"]
        assert not hasattr(app.state, "webhook_v2_dispatcher")
