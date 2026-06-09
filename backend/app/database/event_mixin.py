from pydantic import BaseModel
from sqlalchemy import event as sql_event
from sqlalchemy import inspect


def _track_insert(mapper, connection, target) -> None:
    cls = getattr(target, "create_event_class", None)
    if cls is None:
        return
    from app.core.context import queue_event

    payload = target.to_event()
    field_name = next(iter(cls.model_fields))
    queue_event(cls(**{field_name: payload}))


def _track_update(mapper, connection, target) -> None:
    cls = getattr(target, "update_event_class", None)
    if cls is None:
        return
    from app.core.context import queue_event

    new_payload = target.to_event()
    old_data = new_payload.model_dump()
    for attr in inspect(target).attrs:
        if attr.history.has_changes() and attr.history.deleted and attr.key in old_data:
            old_data[attr.key] = attr.history.deleted[0]
    old_payload = type(new_payload).model_validate(old_data)
    if old_payload != new_payload:
        queue_event(cls(old=old_payload, new=new_payload))


def _track_delete(mapper, connection, target) -> None:
    cls = getattr(target, "delete_event_class", None)
    if cls is None:
        return
    from app.core.context import queue_event

    payload = target.to_event()
    field_name = next(iter(cls.model_fields))
    queue_event(cls(**{field_name: payload}))


class EventTrackedMixin:
    """Mixin that automatically queues V2 webhook events on ORM insert/update/delete.

    Usage:
        class MyModel(Base, EventTrackedMixin):
            create_event_class = MyCreatedEvent
            update_event_class = MyUpdatedEvent
            delete_event_class = MyDeletedEvent

            def to_event(self) -> MyPayload:
                # Only access scalar columns — no relationship traversal.
                return MyPayload(id=self.id, name=self.name, ...)

    Events are flushed to the webhook after a successful HTTP response by
    the ``dispatch_queued_events`` middleware in ``app/main.py``.
    """

    create_event_class: type | None = None
    update_event_class: type | None = None
    delete_event_class: type | None = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        sql_event.listen(cls, "after_insert", _track_insert)
        sql_event.listen(cls, "after_update", _track_update)
        sql_event.listen(cls, "after_delete", _track_delete)

    def to_event(self) -> BaseModel:
        raise NotImplementedError
