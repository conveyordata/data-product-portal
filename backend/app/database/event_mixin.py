from typing import Sequence

from sqlalchemy import event as sql_event

from app.core.context import queue_events
from app.core.webhooks.events import V2Event


class EventTrackedMixin:
    """Mixin that automatically queues V2 webhook events on ORM insert/update/delete.

    Pass the three event classes as keyword arguments on the class definition:

        class MyModel(Base, EventTrackedMixin):

            def to_event(self) -> Event:
                # Only access scalar columns — no relationship traversal.
                return MyPayload(id=self.id, name=self.name, ...)

    The event class should be inherited from V2Event: MyCreatedEvent(V2Event)

    Events are flushed to the webhook after a successful HTTP response by
    the ``dispatch_queued_events`` middleware in ``app/main.py``.
    """

    def __init_subclass__(
        cls,
        **kwargs,
    ):
        super().__init_subclass__(**kwargs)
        sql_event.listen(cls, "after_insert", cls._track)
        sql_event.listen(cls, "after_update", cls._track)
        sql_event.listen(cls, "after_delete", cls._track)

    def to_event(self) -> V2Event:
        raise NotImplementedError

    def generate_extra_events(self, connection) -> Sequence[V2Event]:
        return []

    @staticmethod
    def _track(mapper, connection, target) -> None:
        from app.core.context import queue_event

        queue_event(target.to_event())
        if events := target.generate_extra_events(connection):
            queue_events(events)
