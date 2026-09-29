import pytest

from app.authorization.roles.schema import Scope
from app.authorization.service import OUTPUT_PORT_READER_ROLE
from app.configuration.output_port_access_types.model import (
    OutputPortAccessType,
)
from app.core.authz import Authorization
from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProductVisibility
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.data_products.output_ports.model import OutputPort
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    GlobalRoleAssignmentFactory,
    OutputPortAccessTypeFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/configuration/output_port_access_types"


def payload(name: str, access_function: OutputPortAccessFunction):
    return {"name": name, "description": "", "access_function": access_function.value}


class TestOutputPortAccessTypesRouter:
    @pytest.mark.usefixtures("admin")
    def test_get_output_port_access_types__seeded_with_counts(self, client):
        OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        items = {
            item["name"]: item for item in response.json()["output_port_access_types"]
        }
        assert set(items) == {"Unrestricted", "Restricted", "Private"}
        assert items["Private"]["output_port_count"] == 1
        assert items["Restricted"]["output_port_count"] == 0

    def test_get_output_port_access_types__hides_invite_only_counts(self, client):
        OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        items = {
            item["name"]: item for item in response.json()["output_port_access_types"]
        }
        assert items["Private"]["output_port_count"] == 0

    def test_get_output_port_access_types__config_managers_see_invite_only_counts(
        self, client
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION],
        )
        GlobalRoleAssignmentFactory(identity_id=user.id, role_id=role.id)
        OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        items = {
            item["name"]: item for item in response.json()["output_port_access_types"]
        }
        assert items["Private"]["output_port_count"] == 1

    @pytest.mark.usefixtures("admin")
    def test_create_output_port_access_type__duplicate_name(self, client):
        response = client.post(
            ENDPOINT, json=payload("Restricted", OutputPortAccessFunction.RESTRICTED)
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "An access type with this name already exists."
        )

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_access_type__duplicate_name(self, client):
        access_type = OutputPortAccessTypeFactory(
            name="Internal",
            access_function=OutputPortAccessFunction.RESTRICTED,
        )

        response = client.put(
            f"{ENDPOINT}/{access_type.id}",
            json=payload("Private", OutputPortAccessFunction.RESTRICTED),
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "An access type with this name already exists."
        )

    @pytest.mark.usefixtures("admin")
    def test_create_output_port_access_type(self, client):
        response = client.post(
            ENDPOINT, json=payload("Top Secret", OutputPortAccessFunction.PRIVATE)
        )

        assert response.status_code == 200, response.text
        assert "id" in response.json()

    @pytest.mark.usefixtures("admin")
    def test_create_output_port_access_type__empty_name(self, client):
        response = client.post(
            ENDPOINT, json=payload("  ", OutputPortAccessFunction.PRIVATE)
        )

        assert response.status_code == 422

    def test_create_output_port_access_type__admin_only(self, client):
        response = client.post(
            ENDPOINT, json=payload("Top Secret", OutputPortAccessFunction.PRIVATE)
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_access_type__rename(self, client, session):
        access_type = OutputPortAccessTypeFactory(
            access_function=OutputPortAccessFunction.RESTRICTED
        )

        response = client.put(
            f"{ENDPOINT}/{access_type.id}",
            json=payload("Internal", OutputPortAccessFunction.RESTRICTED),
        )

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(OutputPortAccessType, access_type.id).name == ("Internal")

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_access_type__remap_unused(self, client, session):
        access_type = OutputPortAccessTypeFactory(
            access_function=OutputPortAccessFunction.RESTRICTED
        )

        response = client.put(
            f"{ENDPOINT}/{access_type.id}",
            json=payload("Restricted", OutputPortAccessFunction.UNRESTRICTED),
        )

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(OutputPortAccessType, access_type.id).access_function == (
            OutputPortAccessFunction.UNRESTRICTED
        )

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_access_type__last_invite_only_cannot_be_remapped(
        self, client
    ):
        access_type = OutputPortAccessTypeFactory(
            access_function=OutputPortAccessFunction.PRIVATE
        )

        response = client.put(
            f"{ENDPOINT}/{access_type.id}",
            json=payload("Private", OutputPortAccessFunction.RESTRICTED),
        )

        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_access_type__remap_updates_output_ports(
        self, client, session
    ):
        access_type = OutputPortAccessTypeFactory(
            name="Confidential",
            access_function=OutputPortAccessFunction.RESTRICTED,
        )
        output_port = OutputPortFactory(
            access_function=OutputPortAccessFunction.RESTRICTED,
            access_type=access_type,
        )

        response = client.put(
            f"{ENDPOINT}/{access_type.id}",
            json=payload("Confidential", OutputPortAccessFunction.PRIVATE),
        )

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(OutputPort, output_port.id).access_function == (
            OutputPortAccessFunction.PRIVATE
        )
        assert not Authorization().has_resource_role(
            user_id="*", role_id=OUTPUT_PORT_READER_ROLE, resource_id=output_port.id
        )

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_access_type__remap_blocked_for_hidden_data_product(
        self, client
    ):
        access_type = OutputPortAccessTypeFactory(
            name="Secret", access_function=OutputPortAccessFunction.PRIVATE
        )
        OutputPortFactory(
            access_function=OutputPortAccessFunction.PRIVATE,
            access_type=access_type,
            data_product=DataProductFactory(visibility=DataProductVisibility.HIDDEN),
        )

        response = client.put(
            f"{ENDPOINT}/{access_type.id}",
            json=payload("Secret", OutputPortAccessFunction.RESTRICTED),
        )

        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_update_output_port_access_type__failed_remap_keeps_reader_grants(
        self, client
    ):
        access_type = OutputPortAccessTypeFactory(
            name="Secret", access_function=OutputPortAccessFunction.PRIVATE
        )
        output_port = OutputPortFactory(
            access_function=OutputPortAccessFunction.PRIVATE,
            access_type=access_type,
        )

        response = client.put(
            f"{ENDPOINT}/{access_type.id}",
            json=payload("Restricted", OutputPortAccessFunction.RESTRICTED),
        )

        assert response.status_code == 400
        assert not Authorization().has_resource_role(
            user_id="*", role_id=OUTPUT_PORT_READER_ROLE, resource_id=output_port.id
        )

    def test_update_output_port_access_type__admin_only(self, client):
        access_type = OutputPortAccessTypeFactory(
            access_function=OutputPortAccessFunction.RESTRICTED
        )

        response = client.put(
            f"{ENDPOINT}/{access_type.id}",
            json=payload("Internal", OutputPortAccessFunction.RESTRICTED),
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_remove_output_port_access_type(self, client, session):
        access_type_id = OutputPortAccessTypeFactory(
            name="Unused", access_function=OutputPortAccessFunction.PRIVATE
        ).id

        response = client.delete(f"{ENDPOINT}/{access_type_id}")

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(OutputPortAccessType, access_type_id) is None

    @pytest.mark.usefixtures("admin")
    def test_remove_output_port_access_type__last_invite_only(self, client):
        access_type = OutputPortAccessTypeFactory(
            access_function=OutputPortAccessFunction.PRIVATE
        )

        response = client.delete(f"{ENDPOINT}/{access_type.id}")

        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_remove_output_port_access_type__in_use(self, client):
        access_type = OutputPortAccessTypeFactory(
            name="Used", access_function=OutputPortAccessFunction.PRIVATE
        )
        OutputPortFactory(
            access_function=OutputPortAccessFunction.PRIVATE,
            access_type=access_type,
        )

        response = client.delete(f"{ENDPOINT}/{access_type.id}")

        assert response.status_code == 400

    def test_remove_output_port_access_type__admin_only(self, client):
        access_type = OutputPortAccessTypeFactory(
            name="Unused", access_function=OutputPortAccessFunction.PRIVATE
        )

        response = client.delete(f"{ENDPOINT}/{access_type.id}")

        assert response.status_code == 403
