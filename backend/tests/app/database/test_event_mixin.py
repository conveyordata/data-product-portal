"""Unit tests for EventTrackedMixin.
Uses a lightweight in-memory SQLite model so no database fixtures are needed.
"""

import uuid

import pytest
from pydantic import BaseModel
from sqlalchemy import Column, String, create_engine
from sqlalchemy.dialects.sqlite import TEXT as SQLITE_TEXT
from sqlalchemy.orm import DeclarativeBase, Session

from app.core.context import _pending_events, pop_events
from app.database.event_mixin import EventTrackedMixin


class _Base(DeclarativeBase):
    pass


class _ItemPayload(BaseModel):
    id: str
    name: str


class _ItemCreatedEvent(BaseModel):
    after: _ItemPayload

    @classmethod
    def event_type(cls) -> str:
        return "item.created"


class _ItemUpdatedEvent(BaseModel):
    before: _ItemPayload
    after: _ItemPayload

    @classmethod
    def event_type(cls) -> str:
        return "item.updated"


class _ItemDeletedEvent(BaseModel):
    before: _ItemPayload

    @classmethod
    def event_type(cls) -> str:
        return "item.deleted"


class _Item(
    _Base,
    EventTrackedMixin,
    create_event=_ItemCreatedEvent,
    update_event=_ItemUpdatedEvent,
    delete_event=_ItemDeletedEvent,
):
    __tablename__ = "items"

    id = Column(SQLITE_TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)

    def to_event(self) -> _ItemPayload:
        return _ItemPayload(id=self.id, name=self.name)


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    _Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def event_context():
    """Initialise the ContextVar queue for each test."""
    token = _pending_events.set([])
    yield
    _pending_events.reset(token)


def test_insert_queues_created_event(db):
    item = _Item(id=str(uuid.uuid4()), name="hello")
    db.add(item)
    db.flush()

    events = pop_events()
    assert len(events) == 1
    assert isinstance(events[0], _ItemCreatedEvent)
    assert events[0].after.name == "hello"


def test_update_queues_updated_event(db):
    item = _Item(id=str(uuid.uuid4()), name="before")
    db.add(item)
    db.flush()
    _pending_events.set([])  # discard the created event

    item.name = "after"
    db.flush()

    events = pop_events()
    assert len(events) == 1
    assert isinstance(events[0], _ItemUpdatedEvent)
    assert events[0].before.name == "before"
    assert events[0].after.name == "after"


def test_update_with_no_change_does_not_queue_event(db):
    item = _Item(id=str(uuid.uuid4()), name="same")
    db.add(item)
    db.flush()
    _pending_events.set([])  # discard the created event

    item.name = "same"
    db.flush()

    assert pop_events() == []


def test_delete_queues_deleted_event(db):
    item = _Item(id=str(uuid.uuid4()), name="bye")
    db.add(item)
    db.flush()
    _pending_events.set([])  # discard the created event

    db.delete(item)
    db.flush()

    events = pop_events()
    assert len(events) == 1
    assert isinstance(events[0], _ItemDeletedEvent)
    assert events[0].before.name == "bye"


def test_no_queue_outside_context(db):
    """Events queued outside a request context log a warning and are dropped."""
    _pending_events.set(None)

    item = _Item(id=str(uuid.uuid4()), name="outside")
    db.add(item)
    db.flush()

    with pytest.raises(RuntimeError, match="No event context is open"):
        pop_events()
