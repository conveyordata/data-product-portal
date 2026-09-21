from sqlalchemy import select

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.users.notifications.model import Notification
from app.users.notifications.service import NotificationService
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    EventFactory,
    GroupFactory,
    GroupMembershipFactory,
    MachineUserFactory,
    RoleFactory,
    UserFactory,
)


def test_create_data_product_notifications__resolves_users_and_group_members(
    session,
):
    actor = UserFactory()
    direct_user = UserFactory()
    group_member = UserFactory()
    group = GroupFactory()
    data_product = DataProductFactory()
    role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])

    GroupMembershipFactory(group=group, member=group_member)
    DataProductRoleAssignmentFactory(
        identity_id=direct_user.id,
        data_product_id=data_product.id,
        role_id=role.id,
        requested_by_id=actor.id,
        decided_by_id=actor.id,
    )
    DataProductRoleAssignmentFactory(
        identity_id=group.id,
        data_product_id=data_product.id,
        role_id=role.id,
        requested_by_id=actor.id,
        decided_by_id=actor.id,
    )
    event = EventFactory(actor=actor, subject_id=data_product.id)

    NotificationService(session).create_data_product_notifications(
        data_product_id=data_product.id,
        event_id=event.id,
    )
    session.flush()

    receiver_ids = set(
        session.scalars(
            select(Notification.user_id).where(Notification.event_id == event.id)
        ).all()
    )

    assert receiver_ids == {
        direct_user.id,
        group_member.id,
    }


def test_create_data_product_notifications__deduplicates_recipients(
    session,
):
    actor = UserFactory()
    receiver = UserFactory()
    group = GroupFactory()
    data_product = DataProductFactory()
    role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])

    GroupMembershipFactory(group=group, member=receiver)
    DataProductRoleAssignmentFactory(
        identity_id=receiver.id,
        data_product_id=data_product.id,
        role_id=role.id,
        requested_by_id=actor.id,
        decided_by_id=actor.id,
    )
    DataProductRoleAssignmentFactory(
        identity_id=group.id,
        data_product_id=data_product.id,
        role_id=role.id,
        requested_by_id=actor.id,
        decided_by_id=actor.id,
    )
    event = EventFactory(actor=actor, subject_id=data_product.id)

    NotificationService(session).create_data_product_notifications(
        data_product_id=data_product.id,
        event_id=event.id,
    )
    session.flush()

    notifications = session.scalars(
        select(Notification).where(
            Notification.event_id == event.id,
            Notification.user_id == receiver.id,
        )
    ).all()

    assert len(notifications) == 1


def test_create_data_product_notifications__excludes_machine_users(
    session,
):
    actor = UserFactory()
    machine_user = MachineUserFactory()
    machine_group_member = MachineUserFactory()
    group = GroupFactory()
    data_product = DataProductFactory()
    role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])

    GroupMembershipFactory(group=group, member=machine_group_member)
    DataProductRoleAssignmentFactory(
        identity_id=machine_user.id,
        data_product_id=data_product.id,
        role_id=role.id,
        requested_by_id=actor.id,
        decided_by_id=actor.id,
    )
    DataProductRoleAssignmentFactory(
        identity_id=group.id,
        data_product_id=data_product.id,
        role_id=role.id,
        requested_by_id=actor.id,
        decided_by_id=actor.id,
    )
    event = EventFactory(actor=actor, subject_id=data_product.id)

    NotificationService(session).create_data_product_notifications(
        data_product_id=data_product.id,
        event_id=event.id,
    )
    session.flush()

    notifications = session.scalars(
        select(Notification).where(Notification.event_id == event.id)
    ).all()

    assert notifications == []


def test_create_data_product_notifications__ignores_pending_group_assignments(
    session,
):
    actor = UserFactory()
    group_member = UserFactory()
    group = GroupFactory()
    data_product = DataProductFactory()
    role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])

    GroupMembershipFactory(group=group, member=group_member)
    DataProductRoleAssignmentFactory(
        identity_id=group.id,
        data_product_id=data_product.id,
        role_id=role.id,
        decision=DecisionStatus.PENDING,
        requested_by_id=actor.id,
    )
    event = EventFactory(actor=actor, subject_id=data_product.id)

    NotificationService(session).create_data_product_notifications(
        data_product_id=data_product.id,
        event_id=event.id,
    )
    session.flush()

    notifications = session.scalars(
        select(Notification).where(Notification.event_id == event.id)
    ).all()

    assert notifications == []
