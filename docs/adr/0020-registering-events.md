# How to track and send out events

## Context and Problem Statement
We want to decide on event emission architecture, this is needed for our eventing architecture.

## Decision Drivers

* Where do we want to put the logic to emit events? Currently this is done in routers
*How will we handle DB cascade deletes? We decided a data product delete, would also output events for all Output ports, Technical assets etc

## Considered Options

* **Option 1: Make services responsible** by using a service layer pattern
* **Option 2: Keep the current logic in the routers**
* **Option 3: Listen to ORM events** and use that to emit events

## Decision Outcome

**Chosen option:** *Option 1: Make services responsible*.

### Update 16/6/2026

We have migrated from option 3 to option 1, after starting implementation on Option 3 we noticed that relationschips
aren't loaded on insert. Since these aren't loaded on insert, we can't send out events for these relations. We first
assumed they would available since we load them eagerly on get, but the insert is done before that.
This is a limitation of option 3, and we have decided to go with option 1 instead.

We tried to fix it by registering id's on after_insert, and sending out events on before_commit. But this makes the
outbox pattern we want to implement harder. The resulting code was rather brittle and complex.

Another option is to send out ID only events, which would work, but changes ADR 19 completely, for now we decided on
keeping with ADR 19 and changing this one.

### Confirmation

Because of the simplication of events in [ADR 19](./0019-simplify-events.md) it is quite a nice solution.
It has the advantage that we don't have to change our architecture and can just add this as a mixin to the models we want to track.
It also has the advantage that we can't forget to send out events, because they are automatically triggered by the ORM events.
The limitations should also not hinder us too much, and a migration to other Options can be done 100% without downtime if needed.

## Pros and Cons of the Options

### Option 1: Make services responsible

* **Good, because** a service layer pattern can make a service properly responsible, and we can even mock out the dependencies.
* **Good, because** By using a service layer patern we can easily have a service depend on another service, this can be the event sender service for example.
* **Good, because** We can implement the data product cascade delete by having data product service, call delete on output port service etc. And they will naturally send out events. We can just remove cascade delete in the database
* **Neutral, because** this is a change to the architecture, but we can implement it gradually, this might be confusing
* **Bad, because** As a dev you might forget to send out events

See [example implementation](#example-service-layer-implementation) for how this would look like in practice.

### Option 2: Keep the current logic in the routers

* **Good, because** no changes to the current architecture
* **Bad, because** logic is spread between router and service
* **Bad, because** the data product delete route now has to fetch all output ports etc, and create delete events, which will be error prone. Because we still use cascade delete we might miss something
* **Bad, because** As a dev you might forget to send out events

### Option 3: Listen to ORM events

* **Good, because** of the simplification in events sent out this would actually work quite well
* **Good, because** using the mixin pattern it's still quite clear for users what is happening
* **Good, because** faster to implement
* **Neutral, because** constrains which kind of events can happen. They have to be tied to ORM events as a trigger. But probably this is what we want to keep things simple
* **Neutral, because** When doing bulk updates via SQL and not via SQLAlchemy you will miss events and have to manually send them out. This is however similar to other options 1 and 2 who always have to manually send out events.
* **Bad, because** It happens a bit magically, you wouldn't know by just following along the code. You have to find the mixin
* **Bad, because** `to_event` can only safely access scalar columns already in memory. Since SQLAlchemy is used in async mode, accessing relationships inside `to_event` will raise a `MissingGreenlet` error.
  Lazy loading is forbidden during the synchronous ORM flush event. Any relationship needed in an event must be eagerly loaded (`selectin`/`joined`) on every query that touches that model.
  This is probably not a big deal in practice since we want to send out separate events for links between 2 objects anyway

See [example implementation](#example-after-update-listener) for how this would look like in practice.

## Example service layer implementation

This example shows how services can just be used as dependencies and injected into routers, this means that services
can now include all the logic, where before a service could not easily include another service when needed.

```python
def get_domain_service(db: Session = Depends(get_db_session), event_service: EventService = Depends(get_event_service)) -> "DomainService":
    return DomainService(db, event_service)

@router.put(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_domain(
    id: UUID, domain: DomainUpdate, domain_service: DomainService = Depends(get_domain_service)
) -> UpdateDomainResponse:
    return domain_service.update_domain(id, domain)
```

The `update_domain` function on `DomainService` can now include logic for creating events, which was previously done in the router.


### Example after update listener


This is autogenerated but the gist is:
- Create and EventTrackerMixin class add it to the models we want to track
- Register an create, update, delete event type
- Implement a to_event to create the event pydantic model
- After insert, update, delete trigger are automatically added
- _queue_event can be implemented as contextvar to track events, and can be send out by middleware

```python
class DataProductEvent(BaseModel):
    id: UUID
    name: str
    status: str
    ...

class DataProductUpdateEvent(BaseModel):
    old: DataProductEvent
    new: DataProductEvent

class DataProduct(AbstractDataProduct, EventTrackedMixin):
    update_event_class = DataProductUpdateEvent
    def to_event(self) -> DataProductEvent:
        return DataProductEvent(id=self.id, name=self.name, status=self.status, ...)

class EventTrackedMixin:
    update_event_class: type  # e.g. DataProductUpdateEvent

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        sql_event.listen(cls, "after_insert", _track_insert)
        sql_event.listen(cls, "after_update", _track_update)
        sql_event.listen(cls, "after_delete", _track_delete)

    def to_event(self) -> BaseModel:
        raise NotImplementedError

def _get_old_event(target):
    new_event = target.to_event()
    old_data = new_event.model_dump()
    for attr in inspect(target).attrs:
        if attr.history.has_changes() and attr.history.deleted:
            if attr.key in old_data:
                old_data[attr.key] = attr.history.deleted[0]
    return type(new_event).model_validate(old_data)

def _track_update(mapper, connection, target):
    old = _get_old_event(target)
    new = target.to_event()
    if old != new:
        event = target.update_event_class(old=old, new=new)
        _queue_event(target, event)
```


### Middleware for sending out events

This is an alternative for the annotation on methods, but that annotation can also be used instead.
The advantage of the annotation is that it is easy to generate documentation, and that we can validate expected events
vs unexpected events.

```
# app/core/context.py
from contextvars import ContextVar
from collections.abc import Coroutine

_pending_webhooks: ContextVar[list[EventV2]] = ContextVar("pending_webhooks", default=[])

def add_webhook(event: EventV2) -> None:
    _pending_webhooks.get().append(event)

def pop_webhooks() -> list[EventV2]:
    webhooks = _pending_webhooks.get()
    _pending_webhooks.set([])
    return webhooks
# middleware
async def dispatch(self, request, call_next):
    token = _pending_webhooks.set([])
    response = await call_next(request)

    events = pop_webhooks()
    #Send out all events
    _pending_webhooks.reset(token)
    return response
```

This can be easily extended to save events to a database to support an outbox pattern.


## Useful links:
- [Marc Puig - Notes The Service Layer Pattern](https://mpuig.github.io/Notes/fastapi_basics/04.service_layer_pattern/).
