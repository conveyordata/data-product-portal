from sqlalchemy import select

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.authorization.roles.schema import Scope
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization
from app.data_products.output_ports.announcements.model import Announcement
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.events.enums import EventEntityType, EventType
from app.events.model import Event
from app.settings import settings
from app.users.notifications.model import Notification
from tests.factories import (
    AnnouncementFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetRoleAssignmentFactory,
    ExplorationFactory,
    GroupFactory,
    GroupMembershipFactory,
    InputPortFactory,
    MachineUserFactory,
    NotificationFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/data_products"

PAYLOAD = {
    "type": "action_needed",
    "title": "Daily Feature Engagement will be retired",
    "message": "Move your queries to version 2 before 1 December.",
    "link": "https://docs.example.com/migration",
}


def _url(output_port):
    return f"{ENDPOINT}/{output_port.data_product_id}/output_ports/{output_port.id}/announcements"


def _producer(output_port):
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.DATASET,
        permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
    )
    DatasetRoleAssignmentFactory(
        user_id=user.id, role_id=role.id, output_port_id=output_port.id
    )
    return user


def _consumer(output_port):
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    consumer = DataProductFactory()
    InputPortFactory(consuming_abstract_data_product=consumer, output_port=output_port)
    role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])
    DataProductRoleAssignmentFactory(
        data_product_id=consumer.id, identity_id=user.id, role_id=role.id
    )
    Authorization().add_input_port_link(
        consumer_id=consumer.id,
        producer_data_product_id=output_port.data_product_id,
        producer_output_port_id=output_port.id,
    )
    return user


def _consuming_data_product(output_port, *identities, status=InputPortStatus.APPROVED):
    consumer = DataProductFactory()
    InputPortFactory(
        consuming_abstract_data_product=consumer, output_port=output_port, status=status
    )
    role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])
    for identity in identities:
        DataProductRoleAssignmentFactory(
            data_product_id=consumer.id, identity_id=identity.id, role_id=role.id
        )
    return consumer


def _notified_user_ids(session, announcement_id):
    return set(
        session.scalars(
            select(Notification.user_id)
            .join(Event, Event.id == Notification.event_id)
            .where(Event.target_id == announcement_id)
        ).all()
    )


class TestAnnouncementsRouter:
    def test_create_output_port_announcement__as_producer(self, client, session):
        output_port = OutputPortFactory()
        user = _producer(output_port)

        response = client.post(_url(output_port), json=PAYLOAD)

        assert response.status_code == 200, response.text
        announcement = session.get(Announcement, response.json()["id"])
        assert announcement.title == PAYLOAD["title"]
        assert announcement.link == PAYLOAD["link"]
        assert announcement.author_id == user.id
        event = session.scalar(select(Event).where(Event.target_id == announcement.id))
        assert event.name == EventType.ANNOUNCEMENT_CREATED
        assert event.subject_id == output_port.id
        assert event.target_type == EventEntityType.ANNOUNCEMENT

    def test_create_output_port_announcement__notifies_consumers(self, client, session):
        output_port = OutputPortFactory()
        author = _producer(output_port)
        member = UserFactory()
        group_member = UserFactory()
        group = GroupFactory()
        GroupMembershipFactory(group=group, member=group_member)
        _consuming_data_product(
            output_port, member, group, MachineUserFactory(), author
        )
        exploration = ExplorationFactory()
        InputPortFactory(
            consuming_abstract_data_product=exploration, output_port=output_port
        )

        response = client.post(_url(output_port), json=PAYLOAD)

        assert response.status_code == 200, response.text
        assert _notified_user_ids(session, response.json()["id"]) == {
            member.id,
            group_member.id,
            exploration.owner_id,
        }

    def test_create_output_port_announcement__notifies_member_of_two_consumers_once(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _producer(output_port)
        member = UserFactory()
        _consuming_data_product(output_port, member)
        _consuming_data_product(output_port, member)

        response = client.post(_url(output_port), json=PAYLOAD)

        assert response.status_code == 200, response.text
        notifications = session.scalars(
            select(Notification)
            .join(Event, Event.id == Notification.event_id)
            .where(Event.target_id == response.json()["id"])
        ).all()
        assert [n.user_id for n in notifications] == [member.id]

    def test_create_output_port_announcement__skips_producer_and_unapproved_consumers(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _producer(output_port)
        producer_member = UserFactory()
        DataProductRoleAssignmentFactory(
            data_product_id=output_port.data_product_id,
            identity_id=producer_member.id,
            role_id=RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[]).id,
        )
        _consuming_data_product(
            output_port, UserFactory(), status=InputPortStatus.PENDING
        )
        _consuming_data_product(
            output_port, UserFactory(), status=InputPortStatus.REVOKED
        )

        response = client.post(_url(output_port), json=PAYLOAD)

        assert response.status_code == 200, response.text
        assert _notified_user_ids(session, response.json()["id"]) == set()

    def test_create_output_port_announcement__without_link(self, client, session):
        output_port = OutputPortFactory()
        _producer(output_port)

        response = client.post(_url(output_port), json={**PAYLOAD, "link": None})

        assert response.status_code == 200, response.text
        assert session.get(Announcement, response.json()["id"]).link is None

    def test_create_output_port_announcement__as_consumer_forbidden(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _consumer(output_port)

        response = client.post(_url(output_port), json=PAYLOAD)

        assert response.status_code == 403

    def test_create_output_port_announcement__rejects_non_http_link(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _producer(output_port)

        response = client.post(
            _url(output_port), json={**PAYLOAD, "link": "javascript:alert(1)"}
        )

        assert response.status_code == 422

    def test_create_output_port_announcement__rejects_long_title(self, client, session):
        output_port = OutputPortFactory()
        _producer(output_port)

        response = client.post(_url(output_port), json={**PAYLOAD, "title": "a" * 101})

        assert response.status_code == 422

    def test_create_output_port_announcement__rejects_blank_title(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _producer(output_port)

        response = client.post(_url(output_port), json={**PAYLOAD, "title": "   "})

        assert response.status_code == 422

    def test_create_output_port_announcement__rejects_unknown_type(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _producer(output_port)

        response = client.post(_url(output_port), json={**PAYLOAD, "type": "warning"})

        assert response.status_code == 422

    def test_get_output_port_announcements__as_producer_newest_first(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _producer(output_port)
        client.post(_url(output_port), json={**PAYLOAD, "title": "First"})
        client.post(_url(output_port), json={**PAYLOAD, "title": "Second"})

        response = client.get(_url(output_port))

        assert response.status_code == 200, response.text
        titles = [a["title"] for a in response.json()["announcements"]]
        assert titles == ["Second", "First"]

    def test_get_output_port_announcements__as_consumer(self, client, session):
        output_port = OutputPortFactory()
        AnnouncementFactory(output_port_id=output_port.id)
        _consumer(output_port)

        response = client.get(_url(output_port))

        assert response.status_code == 200, response.text
        assert len(response.json()["announcements"]) == 1

    def test_get_output_port_announcements__as_unrelated_user(self, client, session):
        output_port = OutputPortFactory()
        AnnouncementFactory(output_port_id=output_port.id)
        UserFactory(external_id=settings.DEFAULT_USERNAME)

        response = client.get(_url(output_port))

        assert response.status_code == 200, response.text
        assert len(response.json()["announcements"]) == 1

    def test_get_output_port_announcements__of_private_port_as_unrelated_user_forbidden(
        self, client, session
    ):
        output_port = OutputPortFactory(
            access_function=OutputPortAccessFunction.PRIVATE
        )
        UserFactory(external_id=settings.DEFAULT_USERNAME)

        response = client.get(_url(output_port))

        assert response.status_code == 403

    def test_get_output_port_announcements__as_admin(self, client, session, admin):
        output_port = OutputPortFactory()
        AnnouncementFactory(output_port_id=output_port.id)

        response = client.get(_url(output_port))

        assert response.status_code == 200, response.text
        assert len(response.json()["announcements"]) == 1

    def test_remove_output_port_announcement__as_producer(self, client, session):
        output_port = OutputPortFactory()
        _producer(output_port)
        announcement = AnnouncementFactory(
            output_port_id=output_port.id, author=UserFactory()
        )

        response = client.delete(f"{_url(output_port)}/{announcement.id}")

        assert response.status_code == 200, response.text
        assert client.get(_url(output_port)).json()["announcements"] == []
        event = session.scalar(
            select(Event).where(Event.name == EventType.ANNOUNCEMENT_REMOVED)
        )
        assert event.target_id == announcement.id
        assert event.deleted_target_identifier == announcement.title

    def test_remove_output_port_announcement__keeps_title_on_created_event(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _producer(output_port)
        announcement_id = client.post(_url(output_port), json=PAYLOAD).json()["id"]

        response = client.delete(f"{_url(output_port)}/{announcement_id}")

        assert response.status_code == 200, response.text
        created = session.scalar(
            select(Event).where(
                Event.name == EventType.ANNOUNCEMENT_CREATED,
                Event.target_id == announcement_id,
            )
        )
        session.refresh(created)
        assert created.deleted_target_identifier == PAYLOAD["title"]

    def test_remove_output_port_announcement__removes_its_notifications(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _producer(output_port)
        _consuming_data_product(output_port, UserFactory())
        announcement_id = client.post(_url(output_port), json=PAYLOAD).json()["id"]
        other = NotificationFactory()

        response = client.delete(f"{_url(output_port)}/{announcement_id}")

        assert response.status_code == 200, response.text
        assert _notified_user_ids(session, announcement_id) == set()
        assert session.get(Notification, other.id) is not None

    def test_remove_output_port_announcement__of_other_output_port_not_found(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _producer(output_port)
        announcement = AnnouncementFactory()

        response = client.delete(f"{_url(output_port)}/{announcement.id}")

        assert response.status_code == 404

    def test_remove_output_port_announcement__as_consumer_forbidden(
        self, client, session
    ):
        output_port = OutputPortFactory()
        _consumer(output_port)
        announcement = AnnouncementFactory(output_port_id=output_port.id)

        response = client.delete(f"{_url(output_port)}/{announcement.id}")

        assert response.status_code == 403
