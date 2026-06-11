from contextvars import ContextVar, Token

from pydantic import BaseModel

from app.core.logging import logger

_pending_events: ContextVar[list[BaseModel] | None] = ContextVar(
    "pending_events", default=None
)


def open_event_context() -> Token:
    return _pending_events.set([])


def close_event_context(token: Token) -> None:
    _pending_events.reset(token)


def queue_event(event: BaseModel) -> None:
    lst = _pending_events.get()
    if lst is None:
        logger.warning(
            "Event queued outside of a request context and will be dropped: %s",
            type(event).__name__,
        )
        return
    lst.append(event)


def pop_events() -> list[BaseModel]:
    lst = _pending_events.get()
    if lst is None:
        logger.error("No event context is open")
        raise RuntimeError("No event context is open")
    _pending_events.set(None)
    return lst
