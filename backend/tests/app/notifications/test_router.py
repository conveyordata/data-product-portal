from fastapi.testclient import TestClient
from tests.factories import (
    UserFactory,
)
from tests.factories.notification import NotificationFactory

from app.notifications.schema import Notification
from app.users.schema import User

ENDPOINT = "/api/notifications"


class TestNotificationsRouter:

    def test_get_notifications(self, client: TestClient):
        user: User = UserFactory(external_id="sub")
        notification: Notification = NotificationFactory(user=user)

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(notification.id)

    def test_delete_notification(self, client: TestClient):
        user: User = UserFactory(external_id="sub")
        notification: Notification = NotificationFactory(user=user)

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        response = client.delete(f"{ENDPOINT}/{notification.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_delete_notification_other_user(self, client: TestClient):
        _: User = UserFactory(external_id="sub")
        notification: Notification = NotificationFactory()

        response = client.delete(f"{ENDPOINT}/{notification.id}")
        assert response.status_code == 403

    def test_delete_all_notifications(self, client: TestClient):
        user: User = UserFactory(external_id="sub")
        _: Notification = NotificationFactory(user=user)

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        response = client.delete(f"{ENDPOINT}/all")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 0
