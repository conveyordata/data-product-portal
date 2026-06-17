from pydantic import BaseModel
from sqlalchemy import event as sql_event
from sqlalchemy import inspect


class EventTrackedMixin:
    """Mixin that automatically queues V2 webhook events on ORM insert/update/delete.

    Pass the three event classes as keyword arguments on the class definition:

        class MyModel(Base, EventTrackedMixin,
                      create_event=MyCreatedEvent,
                      update_event=MyUpdatedEvent,
                      delete_event=MyDeletedEvent):

            def to_event(self) -> MyPayload:
                # Only access scalar columns — no relationship traversal.
                return MyPayload(id=self.id, name=self.name, ...)

    The event classes inherit their fields from the payload model
    (e.g. ``class MyCreatedEvent(V2Event, MyPayload)``); the payload returned
    by ``to_event`` is unpacked onto the event when it is queued.

    Events are flushed to the webhook after a successful HTTP response by
    the ``dispatch_queued_events`` middleware in ``app/main.py``.
    """

    create_event_class: type
    update_event_class: type
    delete_event_class: type

    def __init_subclass__(
        cls,
        create_event: type | None = None,
        update_event: type | None = None,
        delete_event: type | None = None,
        **kwargs,
    ):
        super().__init_subclass__(**kwargs)

        if create_event is not None:
            cls.create_event_class = create_event
        if update_event is not None:
            cls.update_event_class = update_event
        if delete_event is not None:
            cls.delete_event_class = delete_event

        missing = [
            name
            for name, attr in (
                ("create_event", "create_event_class"),
                ("update_event", "update_event_class"),
                ("delete_event", "delete_event_class"),
            )
            if not hasattr(cls, attr)
        ]
        if missing:
            raise TypeError(
                f"{cls.__name__} uses EventTrackedMixin but is missing: {', '.join(missing)}. "
                "Pass them as keyword arguments: class MyModel(Base, EventTrackedMixin, "
                "create_event=..., update_event=..., delete_event=...)."
            )

        sql_event.listen(cls, "after_insert", cls._track_insert)
        sql_event.listen(cls, "after_update", cls._track_update)
        sql_event.listen(cls, "after_delete", cls._track_delete)

    def to_event(self) -> BaseModel:
        raise NotImplementedError

    @staticmethod
    def _build_event(event_class: type, target: "EventTrackedMixin"):
        return event_class(**target.to_event().model_dump())

    @staticmethod
    def _track_insert(mapper, connection, target) -> None:
        from app.core.context import queue_event

        queue_event(EventTrackedMixin._build_event(target.create_event_class, target))

    @staticmethod
    def _track_update(mapper, connection, target) -> None:
        from app.core.context import queue_event

        queue_event(EventTrackedMixin._build_event(target.update_event_class, target))

    @staticmethod
    def _track_delete(mapper, connection, target) -> None:
        from app.core.context import queue_event

        queue_event(EventTrackedMixin._build_event(target.delete_event_class, target))
