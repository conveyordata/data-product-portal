from pydantic import BaseModel

from app.core.webhooks.v2 import emit_event, emit_event_after


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
