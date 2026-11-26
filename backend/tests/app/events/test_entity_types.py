from importlib import import_module
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from pydantic import TypeAdapter

from app.events.enums import EventEntityType
from app.events.model import Event
from app.events.schema_response import GetEventHistoryResponseItem
from app.events.service import EventService
from app.identities.schema import IdentityGet
from app.identities.service import get_identity_display_name
from app.users.notifications.model import Notification
from app.users.notifications.service import NotificationService
from app.users.schema import User
from tests import engine
from tests.factories import (
    EventFactory,
    GroupFactory,
    MachineUserFactory,
    NotificationFactory,
    UserFactory,
)


@pytest.mark.parametrize("reader", ["history", "notifications"])
@pytest.mark.parametrize("reference", ["subject", "target"])
def test_event_reads__eager_load_identity_subtypes(session, reader, reference):
    recipient = UserFactory()
    recipient_schema = User.model_validate(recipient)
    resource_id = uuid4()
    adapter = TypeAdapter(IdentityGet | None)
    expected = {}
    other_reference = "target" if reference == "subject" else "subject"
    for factory in (UserFactory, GroupFactory, MachineUserFactory):
        for _ in range(3):
            identity = factory()
            event = EventFactory(
                actor=recipient,
                **{
                    f"{reference}_id": identity.id,
                    f"{reference}_type": EventEntityType.IDENTITY,
                    f"{other_reference}_id": resource_id,
                    f"{other_reference}_type": EventEntityType.DATA_PRODUCT,
                },
            )
            NotificationFactory(event=event, user=recipient)
            expected[event.id] = adapter.dump_python(
                adapter.validate_python(identity), mode="json"
            )
    deleted = UserFactory()
    deleted_event = EventFactory(
        actor=recipient,
        subject_id=resource_id,
        subject_type=EventEntityType.DATA_PRODUCT,
        target_id=deleted.id,
        target_type=EventEntityType.IDENTITY,
    )
    plain_event = EventFactory(
        actor=recipient,
        subject_id=resource_id,
        subject_type=EventEntityType.DATA_PRODUCT,
    )
    for event in (deleted_event, plain_event):
        NotificationFactory(event=event, user=recipient)
        expected[event.id] = None
    session.delete(deleted)
    session.flush()
    session.expunge_all()
    queries = []

    def record(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            queries.append(statement)

    sa.event.listen(engine, "before_cursor_execute", record)
    try:
        if reader == "history":
            events = EventService(session).get_history(
                resource_id, EventEntityType.DATA_PRODUCT
            )
        else:
            events = [
                notification.event
                for notification in NotificationService(session).get_user_notifications(
                    recipient_schema
                )
            ]
        assert len(queries) <= 4
        queries.clear()
        actual = {
            event.id: adapter.dump_python(
                adapter.validate_python(event.identity), mode="json"
            )
            for event in events
        }
        assert actual == expected
        assert queries == []
    finally:
        sa.event.remove(engine, "before_cursor_execute", record)


@pytest.mark.parametrize("entity_type", list(EventEntityType))
def test_event_history_response__uses_current_entity_types(entity_type):
    event = EventFactory(
        subject_type=entity_type, target_id=uuid4(), target_type=entity_type
    )

    response = GetEventHistoryResponseItem.model_validate(event).model_dump(mode="json")

    assert response["subject_type"] == entity_type.value
    assert response["target_type"] == entity_type.value


def test_event_entity_migration__preserves_existing_history(session, monkeypatch):
    event = EventFactory(
        subject_type=EventEntityType.OUTPUT_PORT,
        target_id=uuid4(),
        target_type=EventEntityType.TECHNICAL_ASSET,
    )
    notification = NotificationFactory(event=event)
    event_id = event.id
    actor_id = event.actor_id
    notification_id = notification.id
    migration = import_module(
        "app.database.alembic.versions.2026_10_07_1400-a9203b7e41cd_event_entity_types"
    )
    monkeypatch.setattr(
        migration, "op", Operations(MigrationContext.configure(session.connection()))
    )
    events = sa.table(
        "events",
        sa.column("id", sa.UUID),
        sa.column("subject_type", sa.String),
        sa.column("target_type", sa.String),
    )

    migration.downgrade()

    old_types = session.execute(
        sa.select(events.c.subject_type, events.c.target_type).where(
            events.c.id == event_id
        )
    ).one()
    assert old_types == ("DATASET", "DATA_OUTPUT")

    migration.upgrade()
    session.expire_all()

    restored_event = session.get(Event, event_id)
    assert restored_event is not None
    assert restored_event.subject_type == EventEntityType.OUTPUT_PORT
    assert restored_event.target_type == EventEntityType.TECHNICAL_ASSET
    assert restored_event.actor_id == actor_id
    restored_notification = session.get(Notification, notification_id)
    assert restored_notification is not None
    assert restored_notification.event_id == event_id
    response = GetEventHistoryResponseItem.model_validate(restored_event)
    assert response.subject_type == EventEntityType.OUTPUT_PORT
    assert response.target_type == EventEntityType.TECHNICAL_ASSET


@pytest.mark.parametrize(
    "identity_factory", [UserFactory, GroupFactory, MachineUserFactory]
)
def test_identity_event_migration__preserves_deleted_identity_history(
    session, monkeypatch, identity_factory
):
    identity = identity_factory()
    identity_id = identity.id
    display_name = get_identity_display_name(identity)
    event = EventFactory(
        subject_id=identity_id,
        subject_type=EventEntityType.IDENTITY,
        target_id=identity_id,
        target_type=EventEntityType.IDENTITY,
        deleted_subject_identifier=None,
    )
    event_id = event.id
    session.delete(identity)
    session.flush()
    session.expire_all()
    assert event.subject_type == EventEntityType.IDENTITY
    assert event.target_type == EventEntityType.IDENTITY

    migration = import_module(
        "app.database.alembic.versions."
        "2026_11_23_1437-4b6d2a8f1c35_add_identity_event_reference_entity"
    )
    monkeypatch.setattr(
        migration, "op", Operations(MigrationContext.configure(session.connection()))
    )
    migration.downgrade()
    session.refresh(event)
    assert event.subject_type == EventEntityType.USER
    assert event.target_type == EventEntityType.USER
    migration.upgrade()
    session.expire_all()

    preserved_event = session.get(Event, event_id)
    assert preserved_event is not None
    assert preserved_event.subject_type == EventEntityType.IDENTITY
    assert preserved_event.target_type == EventEntityType.IDENTITY
    assert preserved_event.subject_id == identity_id
    assert preserved_event.target_id == identity_id
    assert preserved_event.deleted_subject_identifier == display_name
    assert preserved_event.deleted_target_identifier == display_name
    assert preserved_event.identity is None


@pytest.mark.parametrize("deleted", [False, True])
def test_identity_event_migration__converts_existing_user_references(
    session, monkeypatch, deleted
):
    user = UserFactory()
    user_id, email = user.id, user.email
    event = EventFactory(
        subject_id=user_id,
        subject_type=EventEntityType.USER,
        target_id=user_id,
        target_type=EventEntityType.USER,
        deleted_subject_identifier=None,
    )
    other_event = EventFactory(
        subject_type=EventEntityType.OUTPUT_PORT,
        target_id=uuid4(),
        target_type=EventEntityType.TECHNICAL_ASSET,
    )
    event_id, actor_id, created_on = event.id, event.actor_id, event.created_on
    if deleted:
        session.delete(user)
        session.flush()
    migration = import_module(
        "app.database.alembic.versions."
        "2026_11_23_1437-4b6d2a8f1c35_add_identity_event_reference_entity"
    )
    monkeypatch.setattr(
        migration, "op", Operations(MigrationContext.configure(session.connection()))
    )
    migration.downgrade()

    migration.upgrade()
    session.refresh(event)
    session.refresh(other_event)

    assert event.id == event_id
    assert event.subject_type == EventEntityType.IDENTITY
    assert event.target_type == EventEntityType.IDENTITY
    assert event.subject_id == user_id
    assert event.target_id == user_id
    assert event.actor_id == actor_id
    assert event.created_on == created_on
    assert event.deleted_subject_identifier == (email if deleted else None)
    assert event.deleted_target_identifier == (email if deleted else None)
    assert other_event.subject_type == EventEntityType.OUTPUT_PORT
    assert other_event.target_type == EventEntityType.TECHNICAL_ASSET
