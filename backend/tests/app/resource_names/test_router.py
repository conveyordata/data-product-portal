import pytest
from fastapi import HTTPException
from starlette.testclient import TestClient

from app.resource_names.router import validate_resource_name
from app.resource_names.service import ResourceNameValidityType
from tests.factories import DomainFactory, ExplorationFactory


class TestResourceNamesRouter:
    @staticmethod
    def validate_namespace(client: TestClient, namespace: str, model: str):
        return client.get(
            "api/v2/resource_names/validate",
            params={"resource_name": namespace, "model": model},
        )

    def test_validated_exploration(self, client):
        namespace = "test"
        response = self.validate_namespace(client, namespace, "exploration")
        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.VALID

    def test_validate_exploration_duplicate_namespaces(self, client: TestClient):
        namespace = "namespace"
        ExplorationFactory(namespace=namespace)

        response = self.validate_namespace(client, namespace, "exploration")
        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.DUPLICATE

    def test_validate_resource_name__duplicate_domain_namespace(
        self, client: TestClient
    ):
        namespace = "finance"
        DomainFactory(namespace=namespace)

        response = self.validate_namespace(client, namespace, "domain")
        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.DUPLICATE

    @pytest.mark.parametrize("namespace", [".", "..", "..."])
    def test_validate_resource_name__dots_only_domain_namespace(
        self, client: TestClient, namespace
    ):
        response = self.validate_namespace(client, namespace, "domain")
        assert response.json()["validity"] == (
            ResourceNameValidityType.INVALID_CHARACTERS
        )

    @pytest.mark.parametrize("name", ["...", "-..-"])
    def test_sanitize_resource_name__dots_only_suggests_nothing(
        self, client: TestClient, name
    ):
        response = client.get("api/v2/resource_names/sanitize", params={"name": name})
        assert response.json()["resource_name"] == ""

    def test_validate_resource_name(self):
        """
        This test exists to ensure the case is tested where we have added a new model to the enum
        but forgot to implement it. This ensures we have 100% coverage of this router
        """
        with pytest.raises(HTTPException):
            validate_resource_name("bla", "unknown model")  # type: ignore[arg-type]
