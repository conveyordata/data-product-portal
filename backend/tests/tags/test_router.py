import pytest
from tests.factories import TagFactory
from tests.factories.data_output import DataOutputFactory
from tests.factories.data_product import DataProductFactory
from tests.factories.dataset import DatasetFactory

ENDPOINT = "/api/tags"


@pytest.fixture
def tags_payload():
    return {"value": "Test"}


class TestTagsRouter:
    @pytest.mark.usefixtures("admin")
    def test_create_tag(self, tags_payload, client):
        response = self.create_tag(client, tags_payload)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_tags(self, client):
        TagFactory()
        tags = self.get_tags(client)
        assert tags.status_code == 200
        assert len(tags.json()) == 1

    @pytest.mark.usefixtures("admin")
    def test_update_tag(self, client):
        tag = TagFactory()
        response = self.update_tag(client, {"value": "update"}, tag.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(tag.id)

    @pytest.mark.usefixtures("admin")
    def test_remove_tag(self, client):
        tag = TagFactory()
        response = self.remove_tag(client, tag.id)
        assert response.status_code == 200

        tags = self.get_tags(client)
        assert tags.status_code == 200
        assert len(tags.json()) == 0

    @pytest.mark.usefixtures("admin")
    def test_remove_tag_coupled_with_dataset(self, client):
        tag = TagFactory()
        DatasetFactory(tags=[tag])
        response = self.remove_tag(client, tag.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_remove_tag_coupled_with_data_product(self, client):
        tag = TagFactory()
        DataProductFactory(tags=[tag])
        response = self.remove_tag(client, tag.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_remove_tag_coupled_with_data_output(self, client):
        tag = TagFactory()
        DataOutputFactory(tags=[tag])
        response = self.remove_tag(client, tag.id)
        assert response.status_code == 200

    def test_create_tag_admin_only(self, tags_payload, client):
        response = self.create_tag(client, tags_payload)
        assert response.status_code == 403

    def test_update_tag_admin_only(self, client):
        tag = TagFactory()
        response = self.update_tag(client, {"value": "update"}, tag.id)
        assert response.status_code == 403

    def test_remove_tag_admin_only(self, client):
        tag = TagFactory()
        response = self.remove_tag(client, tag.id)
        assert response.status_code == 403

    @staticmethod
    def create_tag(client, payload):
        return client.post(ENDPOINT, json=payload)

    @staticmethod
    def update_tag(client, payload, tag_id):
        return client.put(f"{ENDPOINT}/{tag_id}", json=payload)

    @staticmethod
    def remove_tag(client, tag_id):
        return client.delete(f"{ENDPOINT}/{tag_id}")

    @staticmethod
    def get_tags(client):
        return client.get(ENDPOINT)
