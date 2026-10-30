import pytest
from fastapi.testclient import TestClient

from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.events.enums import EventEntityType, EventType
from app.settings import settings
from tests.factories import (
    AnnouncementFactory,
    EventFactory,
    NotificationFactory,
    OutputPortFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/users/current/notifications"


class TestNotificationsRouter:
    def test_get_notifications(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        notification = NotificationFactory(user=user)

        response = client.get(ENDPOINT)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["id"] == str(notification.id)

    def test_get_notifications__announcement(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        output_port = OutputPortFactory()
        announcement = AnnouncementFactory(output_port_id=output_port.id)
        event = EventFactory(
            name=EventType.ANNOUNCEMENT_CREATED,
            subject_id=output_port.id,
            subject_type=EventEntityType.OUTPUT_PORT,
            deleted_subject_identifier=None,
            target_id=announcement.id,
            target_type=EventEntityType.ANNOUNCEMENT,
        )
        NotificationFactory(user=user, event=event)

        response = client.get(ENDPOINT)

        assert response.status_code == 200, response.text
        event_json = response.json()["notifications"][0]["event"]
        assert event_json["announcement"]["title"] == announcement.title
        assert event_json["announcement"]["type"] == announcement.type
        assert event_json["output_port"]["name"] == output_port.name
        assert event_json["output_port"]["data_product_id"] == str(
            output_port.data_product_id
        )

    def test_get_notifications__skips_announcement_of_unreadable_output_port(
        self, client: TestClient
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        output_port = OutputPortFactory(
            access_function=OutputPortAccessFunction.PRIVATE
        )
        announcement = AnnouncementFactory(output_port_id=output_port.id)
        event = EventFactory(
            name=EventType.ANNOUNCEMENT_CREATED,
            subject_id=output_port.id,
            subject_type=EventEntityType.OUTPUT_PORT,
            target_id=announcement.id,
            target_type=EventEntityType.ANNOUNCEMENT,
        )
        NotificationFactory(user=user, event=event)
        other = NotificationFactory(user=user)

        response = client.get(ENDPOINT)

        assert response.status_code == 200, response.text
        assert [n["id"] for n in response.json()["notifications"]] == [str(other.id)]

    def test_get_notifications__skips_announcement_of_deleted_output_port(
        self, client: TestClient, admin
    ):
        user = admin
        output_port = OutputPortFactory()
        announcement = AnnouncementFactory(output_port_id=output_port.id)
        event = EventFactory(
            name=EventType.ANNOUNCEMENT_CREATED,
            subject_id=output_port.id,
            subject_type=EventEntityType.OUTPUT_PORT,
            target_id=announcement.id,
            target_type=EventEntityType.ANNOUNCEMENT,
        )
        NotificationFactory(user=user, event=event)
        other = NotificationFactory(user=user)
        delete_response = client.delete(
            f"/api/v2/data_products/{output_port.data_product_id}/output_ports/{output_port.id}"
        )
        assert delete_response.status_code == 200, delete_response.text

        response = client.get(ENDPOINT)

        assert response.status_code == 200, response.text
        assert [n["id"] for n in response.json()["notifications"]] == [str(other.id)]

    def test_delete_notification(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        notification = NotificationFactory(user=user)

        response = client.get(ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 1

        response = self.delete_notification(client, notification.id)
        assert response.status_code == 200

        response = client.get(ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()["notifications"]) == 0

    def test_delete_notification_other_user(self, client: TestClient):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        notification = NotificationFactory()

        response = self.delete_notification(client, notification.id)
        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_delete_notification_other_user_as_admin(self, client: TestClient):
        notification = NotificationFactory()

        response = self.delete_notification(client, notification.id)
        assert response.status_code == 200

    def test_delete_all_notifications(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        NotificationFactory(user=user)

        response = client.get(ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 1

        response = client.delete(f"{ENDPOINT}/all")
        assert response.status_code == 200

        response = client.get(ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()["notifications"]) == 0

    @staticmethod
    def delete_notification(client: TestClient, notification_id):
        return client.delete(f"{ENDPOINT}/{notification_id}")
