import pytest
from tests.factories import TagFactory

ENDPOINT = "/api/tags"


@pytest.fixture
def tags_payload():
    return {"value": "Test"}


class TestTagsRouter:
    def test_create_tag(self, tags_payload, client):
        response = client.post(ENDPOINT, json=tags_payload)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_tags(self, client):
        TagFactory()
        tags = client.get(ENDPOINT)
        assert tags.status_code == 200
        assert len(tags.json()) == 1

    def test_update_tag(self, client):
        tag = TagFactory()
        response = client.put(f"{ENDPOINT}/{tag.id}", json={"value": "Updated"})
        assert response.status_code == 200
        assert response.json()["id"] == str(tag.id)

    def test_remove_tag(self, client):
        tag = TagFactory()
        response = client.delete(f"{ENDPOINT}/{tag.id}")
        assert response.status_code == 200

        tags = client.get(ENDPOINT)
        assert tags.status_code == 200
        assert len(tags.json()) == 0
