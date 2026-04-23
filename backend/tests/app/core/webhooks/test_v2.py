import asyncio  # noqa: F401

import pytest
from pydantic import BaseModel

from app.core.webhooks.events import V2Event
from app.core.webhooks.v2 import emit_event, emit_event_after


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


def test_v2event_subclass_without_event_type_raises():
    with pytest.raises(TypeError, match="must define an event_type"):

        class _Bad(V2Event):
            value: str


def test_v2event_subclass_with_event_type_ok():
    assert _SampleV2Event.event_type() == "sample.event"


# EXISTING: original tests below


class _SampleEvent(BaseModel):
    value: str


def test_emit_event_stamps_event_type():
    dep = emit_event("foo.bar", _SampleEvent, lambda **_: {})
    assert dep._webhook_event_type == "foo.bar"


def test_emit_event_stamps_payload_model():
    dep = emit_event("foo.bar", _SampleEvent, lambda **_: {})
    assert dep._webhook_payload_model is _SampleEvent


def test_emit_event_after_stamps_event_type():
    dep = emit_event_after("foo.baz", _SampleEvent, lambda **_: {})
    assert dep._webhook_event_type == "foo.baz"


def test_emit_event_after_stamps_payload_model():
    dep = emit_event_after("foo.baz", _SampleEvent, lambda **_: {})
    assert dep._webhook_payload_model is _SampleEvent
