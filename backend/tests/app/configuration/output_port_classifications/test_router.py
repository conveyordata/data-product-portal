import pytest

from app.authorization.roles.schema import Scope
from app.authorization.service import OUTPUT_PORT_READER_ROLE
from app.configuration.output_port_classifications.model import (
    OutputPortClassification,
)
from app.core.authz import Authorization
from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProductVisibility
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import OutputPort
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    GlobalRoleAssignmentFactory,
    OutputPortClassificationFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/configuration/output_port_classifications"


def payload(name: str, access_type: OutputPortAccessType):
    return {"name": name, "description": "", "access_type": access_type.value}


class TestOutputPortClassificationsRouter:
    @pytest.mark.usefixtures("admin")
    def test_get_output_port_classifications__seeded_with_counts(self, client):
        OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        items = {
            item["name"]: item
            for item in response.json()["output_port_classifications"]
        }
        assert set(items) == {"Unrestricted", "Restricted", "Private"}
        assert items["Private"]["output_port_count"] == 1
        assert items["Restricted"]["output_port_count"] == 0

    def test_get_output_port_classifications__hides_invite_only_counts(self, client):
        OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        items = {
            item["name"]: item
            for item in response.json()["output_port_classifications"]
        }
        assert items["Private"]["output_port_count"] == 0

    def test_get_output_port_classifications__config_managers_see_invite_only_counts(
        self, client
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION],
        )
        GlobalRoleAssignmentFactory(identity_id=user.id, role_id=role.id)
        OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        items = {
            item["name"]: item
            for item in response.json()["output_port_classifications"]
        }
        assert items["Private"]["output_port_count"] == 1

    @pytest.mark.usefixtures("admin")
    def test_create_output_port_classification__duplicate_name(self, client):
        response = client.post(
            ENDPOINT, json=payload("Restricted", OutputPortAccessType.RESTRICTED)
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "A classification with this name already exists."
        )

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_classification__duplicate_name(self, client):
        classification = OutputPortClassificationFactory(
            name="Internal",
            access_type=OutputPortAccessType.RESTRICTED,
        )

        response = client.put(
            f"{ENDPOINT}/{classification.id}",
            json=payload("Private", OutputPortAccessType.RESTRICTED),
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "A classification with this name already exists."
        )

    @pytest.mark.usefixtures("admin")
    def test_create_output_port_classification(self, client):
        response = client.post(
            ENDPOINT, json=payload("VITO Secret", OutputPortAccessType.PRIVATE)
        )

        assert response.status_code == 200, response.text
        assert "id" in response.json()

    def test_create_output_port_classification__admin_only(self, client):
        response = client.post(
            ENDPOINT, json=payload("VITO Secret", OutputPortAccessType.PRIVATE)
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_classification__rename(self, client, session):
        classification = OutputPortClassificationFactory(
            access_type=OutputPortAccessType.RESTRICTED
        )

        response = client.put(
            f"{ENDPOINT}/{classification.id}",
            json=payload("Internal", OutputPortAccessType.RESTRICTED),
        )

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(OutputPortClassification, classification.id).name == (
            "Internal"
        )

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_classification__remap_unused(self, client, session):
        classification = OutputPortClassificationFactory(
            access_type=OutputPortAccessType.RESTRICTED
        )

        response = client.put(
            f"{ENDPOINT}/{classification.id}",
            json=payload("Restricted", OutputPortAccessType.UNRESTRICTED),
        )

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(OutputPortClassification, classification.id).access_type == (
            OutputPortAccessType.UNRESTRICTED
        )

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_classification__last_invite_only_cannot_be_remapped(
        self, client
    ):
        classification = OutputPortClassificationFactory(
            access_type=OutputPortAccessType.PRIVATE
        )

        response = client.put(
            f"{ENDPOINT}/{classification.id}",
            json=payload("Private", OutputPortAccessType.RESTRICTED),
        )

        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_classification__remap_updates_output_ports(
        self, client, session
    ):
        classification = OutputPortClassificationFactory(
            name="Confidential",
            access_type=OutputPortAccessType.RESTRICTED,
        )
        output_port = OutputPortFactory(
            access_type=OutputPortAccessType.RESTRICTED, classification=classification
        )

        response = client.put(
            f"{ENDPOINT}/{classification.id}",
            json=payload("Confidential", OutputPortAccessType.PRIVATE),
        )

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(OutputPort, output_port.id).access_type == (
            OutputPortAccessType.PRIVATE
        )
        assert not Authorization().has_resource_role(
            user_id="*", role_id=OUTPUT_PORT_READER_ROLE, resource_id=output_port.id
        )

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_classification__remap_blocked_for_hidden_data_product(
        self, client
    ):
        classification = OutputPortClassificationFactory(
            name="Secret", access_type=OutputPortAccessType.PRIVATE
        )
        OutputPortFactory(
            access_type=OutputPortAccessType.PRIVATE,
            classification=classification,
            data_product=DataProductFactory(visibility=DataProductVisibility.HIDDEN),
        )

        response = client.put(
            f"{ENDPOINT}/{classification.id}",
            json=payload("Secret", OutputPortAccessType.RESTRICTED),
        )

        assert response.status_code == 400

    def test_update_output_port_classification__admin_only(self, client):
        classification = OutputPortClassificationFactory(
            access_type=OutputPortAccessType.RESTRICTED
        )

        response = client.put(
            f"{ENDPOINT}/{classification.id}",
            json=payload("Internal", OutputPortAccessType.RESTRICTED),
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_remove_output_port_classification(self, client, session):
        classification_id = OutputPortClassificationFactory(
            name="Unused", access_type=OutputPortAccessType.PRIVATE
        ).id

        response = client.delete(f"{ENDPOINT}/{classification_id}")

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(OutputPortClassification, classification_id) is None

    @pytest.mark.usefixtures("admin")
    def test_remove_output_port_classification__last_invite_only(self, client):
        classification = OutputPortClassificationFactory(
            access_type=OutputPortAccessType.PRIVATE
        )

        response = client.delete(f"{ENDPOINT}/{classification.id}")

        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_remove_output_port_classification__in_use(self, client):
        classification = OutputPortClassificationFactory(
            name="Used", access_type=OutputPortAccessType.PRIVATE
        )
        OutputPortFactory(
            access_type=OutputPortAccessType.PRIVATE, classification=classification
        )

        response = client.delete(f"{ENDPOINT}/{classification.id}")

        assert response.status_code == 400

    def test_remove_output_port_classification__admin_only(self, client):
        classification = OutputPortClassificationFactory(
            name="Unused", access_type=OutputPortAccessType.PRIVATE
        )

        response = client.delete(f"{ENDPOINT}/{classification.id}")

        assert response.status_code == 403
