import pytest
from fastapi.testclient import TestClient

from app.settings import settings
from tests.factories import NotificationFactory, UserFactory

OLD_ENDPOINT = "/api/notifications"
ENDPOINT = "/api/v2/users/current/notifications"


class TestNotificationsRouter:
    def test_get_notifications_old(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        notification = NotificationFactory(user=user)

        response = client.get(OLD_ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(notification.id)

    def test_get_notifications(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        notification = NotificationFactory(user=user)

        response = client.get(ENDPOINT)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["id"] == str(notification.id)

    def test_delete_notification(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        notification = NotificationFactory(user=user)

        response = client.get(OLD_ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        response = self.delete_notification(client, notification.id)
        assert response.status_code == 200

        response = client.get(OLD_ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()) == 0

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

        response = client.get(OLD_ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        response = client.delete(f"{OLD_ENDPOINT}/all")
        assert response.status_code == 200

        response = client.get(OLD_ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()) == 0

    @staticmethod
    def delete_notification(client: TestClient, notification_id):
        return client.delete(f"{OLD_ENDPOINT}/{notification_id}")
