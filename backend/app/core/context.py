from contextvars import ContextVar

from pydantic import BaseModel

# None = no active request context; events queued outside a request are silently dropped.
_pending_events: ContextVar[list[BaseModel] | None] = ContextVar(
    "pending_events", default=None
)


def queue_event(event: BaseModel) -> None:
    lst = _pending_events.get()
    if lst is not None:
        lst.append(event)


def pop_events() -> list[BaseModel]:
    lst = _pending_events.get()
    if lst is None:
        return []
    _pending_events.set([])
    return lst
