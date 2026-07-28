from contextvars import ContextVar, Token
from typing import Sequence

from app.core.logging import logger
from app.core.webhooks.events import V2Event

_pending_events: ContextVar[list[V2Event] | None] = ContextVar(
    "pending_events", default=None
)


def open_event_context() -> Token:
    return _pending_events.set([])


def close_event_context(token: Token) -> None:
    _pending_events.reset(token)


def queue_events(events: Sequence[V2Event]) -> None:
    lst = _pending_events.get()
    if lst is None:
        logger.warning(
            "Events queued outside of a request context and will be dropped: %s",
            [type(event).__name__ for event in events],
        )
        return
    lst.extend(events)


def queue_event(event: V2Event) -> None:
    queue_events([event])


def pop_events() -> list[V2Event]:
    lst = _pending_events.get()
    if lst is None:
        logger.error("No event context is open")
        raise RuntimeError("No event context is open")
    _pending_events.set(None)
    return lst
