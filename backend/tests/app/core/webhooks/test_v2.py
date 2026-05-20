import asyncio

import pytest

from app.core.webhooks.events import V2Event
from app.core.webhooks.v2 import _emits_event


class _SampleV2Event(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "sample.event"

    value: str


def _make_request(**state_attrs):
    """Return a minimal mock request-like object with a State."""
    from unittest.mock import MagicMock

    from starlette.datastructures import State
    from starlette.requests import Request as _R

    req = MagicMock(spec=_R)
    state = State()
    for k, v in state_attrs.items():
        setattr(state, k, v)
    req.state = state
    return req


def test_v2event_subclass_without_event_type_raises() -> None:
    with pytest.raises(TypeError, match="must define an event_type"):

        class _Bad(V2Event):
            value: str


def test_v2event_subclass_with_event_type_ok():
    assert _SampleV2Event.event_type() == "sample.event"


# _emits_event factory tests


def test_emits_event_stamps_event_type():
    dep = _emits_event(_SampleV2Event)
    assert dep._webhook_event_type == "sample.event"


def test_emits_event_stamps_payload_model():
    dep = _emits_event(_SampleV2Event)
    assert dep._webhook_payload_model is _SampleV2Event


def test_emits_event_raises_if_state_event_not_set():
    """Handler forgot to set request.state.event → RuntimeError after yield."""
    dep = _emits_event(_SampleV2Event)
    request = _make_request()  # no 'event' in state

    async def _run():
        gen = dep(request)
        await gen.__anext__()  # advance to yield (simulate handler running)
        await gen.__anext__()  # continue — else block runs → raises RuntimeError

    with pytest.raises(RuntimeError, match="did not set request.state.event"):
        asyncio.run(_run())


def test_emits_event_raises_if_wrong_event_type() -> None:
    """Handler set wrong event type → TypeError after yield."""

    class _OtherEvent(V2Event):
        @classmethod
        def event_type(cls) -> str:
            return "other.event"

        value: str

    dep = _emits_event(_SampleV2Event)
    request = _make_request(event=_OtherEvent(value="x"))

    async def _run():
        gen = dep(request)
        await gen.__anext__()
        await gen.__anext__()

    with pytest.raises(TypeError, match="Expected _SampleV2Event"):
        asyncio.run(_run())


def test_emits_event_does_not_emit_on_handler_failure():
    """If handler raises, the else block is skipped — no webhook call."""
    dep = _emits_event(_SampleV2Event)
    request = _make_request()

    async def _run():
        gen = dep(request)
        await gen.__anext__()
        await gen.athrow(ValueError("handler blew up"))

    with pytest.raises(ValueError, match="handler blew up"):
        asyncio.run(_run())
    # If we reach here the exception propagated correctly and else was skipped.
