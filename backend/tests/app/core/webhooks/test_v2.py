import pytest

from app.core.webhooks.events import V2Event


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
