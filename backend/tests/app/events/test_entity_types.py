from importlib import import_module
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from app.events.enums import EventEntityType
from app.events.model import Event
from app.events.schema_response import GetEventHistoryResponseItem
from app.users.model import User
from app.users.notifications.model import Notification
from tests.factories import (
    EventFactory,
    GroupFactory,
    MachineUserFactory,
    NotificationFactory,
    UserFactory,
)


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
def test_identity_event_migration__handles_deleted_identities(
    session, monkeypatch, identity_factory
):
    identity = identity_factory()
    event = EventFactory(
        subject_id=identity.id,
        subject_type=EventEntityType.IDENTITY,
        target_id=identity.id,
        target_type=EventEntityType.IDENTITY,
        deleted_subject_identifier=None,
    )
    event_id = event.id
    identity_id = identity.id
    is_user = isinstance(identity, User)
    identifier = identity.email if is_user else identity.display_name
    session.delete(identity)
    session.flush()
    migration = import_module(
        "app.database.alembic.versions."
        "2026_11_16_1501-4b6d2a8f1c35_add_identity_event_reference_entity"
    )
    monkeypatch.setattr(
        migration, "op", Operations(MigrationContext.configure(session.connection()))
    )

    if is_user:
        migration.downgrade()
        migration.upgrade()
    else:
        with (
            pytest.raises(
                sa.exc.DBAPIError,
                match="Cannot downgrade while non-user identity events exist",
            ),
            session.connection().begin_nested(),
        ):
            migration.downgrade()

    session.expire_all()
    preserved_event = session.get(Event, event_id)
    assert preserved_event is not None
    expected_type = EventEntityType.USER if is_user else EventEntityType.IDENTITY
    assert preserved_event.subject_type == expected_type
    assert preserved_event.target_type == expected_type
    assert preserved_event.subject_id == identity_id
    assert preserved_event.target_id == identity_id
    assert preserved_event.deleted_subject_identifier == identifier
    assert preserved_event.deleted_target_identifier == identifier
