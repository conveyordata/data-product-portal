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
    def _track_insert(mapper, connection, target) -> None:
        from app.core.context import queue_event

        payload = target.to_event()
        field_name = next(iter(target.create_event_class.model_fields))
        queue_event(target.create_event_class(**{field_name: payload}))

    @staticmethod
    def _track_update(mapper, connection, target) -> None:
        from app.core.context import queue_event

        new_payload = target.to_event()
        old_data = new_payload.model_dump()
        for attr in inspect(target).attrs:
            if (
                attr.history.has_changes()
                and attr.history.deleted
                and attr.key in old_data
            ):
                old_data[attr.key] = attr.history.deleted[0]
        old_payload = type(new_payload).model_validate(old_data)
        if old_payload != new_payload:
            queue_event(
                target.update_event_class(before=old_payload, after=new_payload)
            )

    @staticmethod
    def _track_delete(mapper, connection, target) -> None:
        from app.core.context import queue_event

        payload = target.to_event()
        field_name = next(iter(target.delete_event_class.model_fields))
        queue_event(target.delete_event_class(**{field_name: payload}))
