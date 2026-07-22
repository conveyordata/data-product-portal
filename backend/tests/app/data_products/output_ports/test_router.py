from copy import deepcopy
from uuid import uuid4

import pytest

from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.authorization.roles.schema import Scope
from app.core.authz.actions import AuthorizationAction
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import Dataset
from app.events.enums import EventReferenceEntity
from app.events.service import EventService
from app.resource_names.service import ResourceNameValidityType
from app.settings import settings
from tests import test_session
from tests.factories import (
    AccessDurationFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DataProductSettingFactory,
    DatasetRoleAssignmentFactory,
    DomainFactory,
    ExplorationFactory,
    GlobalRoleAssignmentFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    TechnicalAssetFactory,
    TechnicalAssetOutputPortAssociationFactory,
    UserFactory,
)
from tests.webhook_util import assert_event_in_queue

ENDPOINT = "/api/v2/data_products/{}/output_ports"


@pytest.fixture
def dataset_payload():
    user = UserFactory()
    domain = DomainFactory()
    data_product = DataProductFactory()
    return {
        "name": "Test Dataset",
        "description": "Test Description",
        "namespace": "test-dataset",
        "tag_ids": [],
        "owners": [
            str(user.id),
        ],
        "access_type": OutputPortAccessType.RESTRICTED.value,
        "domain_id": str(domain.id),
        "data_product_id": str(data_product.id),
        "exploration_access_duration_type": AccessDurationType.TIME_BOUND.value,
        "data_product_access_duration_type": AccessDurationType.TIME_BOUND.value,
    }


@pytest.fixture
def output_port_event_payload():
    user = UserFactory()
    return {
        "name": "Test Output Port",
        "description": "Test Description",
        "namespace": "test-op-event-ns",
        "tag_ids": [],
        "owners": [str(user.id)],
        "access_type": "restricted",
    }


class TestOutputPortRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_create_dataset(self, dataset_payload, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        created_dataset = self.create_output_port(
            client, dataset_payload["data_product_id"], dataset_payload
        )
        assert created_dataset.status_code == 200, created_dataset.text
        assert "id" in created_dataset.json()

    def test_create_output_port(self, session, dataset_payload, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        data_product_id = dataset_payload.pop("data_product_id")
        created_dataset = self.create_output_port(
            client, data_product_id, dataset_payload
        )
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

    def test_create_output_port_type_public(
        self, session, dataset_payload, client
    ) -> None:
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        data_product_id = dataset_payload.pop("data_product_id")
        dataset_payload["access_type"] = OutputPortAccessType.PUBLIC.value
        created_dataset = self.create_output_port(
            client, data_product_id, dataset_payload
        )
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()
        output_port: Dataset = (
            session.query(Dataset).filter_by(id=created_dataset.json()["id"]).first()
        )
        assert output_port.access_type == OutputPortAccessType.UNRESTRICTED.value

    def test_create_dataset_no_owners(self, session, dataset_payload, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        create_payload = deepcopy(dataset_payload)
        create_payload["owners"] = []
        created_dataset = self.create_output_port(
            client, create_payload["data_product_id"], create_payload
        )
        assert created_dataset.status_code == 422

    def test_create_dataset_duplicate_namespace(self, session, dataset_payload, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        OutputPortFactory(namespace=dataset_payload["namespace"])

        created_dataset = self.create_output_port(
            client, dataset_payload["data_product_id"], dataset_payload
        )
        assert created_dataset.status_code == 400

    def test_create_dataset_invalid_characters_namespace(
        self, session, dataset_payload, client
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        create_payload = deepcopy(dataset_payload)
        create_payload["namespace"] = "!"

        created_dataset = self.create_output_port(
            client, create_payload["data_product_id"], create_payload
        )
        assert created_dataset.status_code == 400

    def test_create_dataset_invalid_length_namespace(
        self, session, dataset_payload, client
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        create_payload = deepcopy(dataset_payload)
        create_payload["namespace"] = "a" * 256

        created_dataset = self.create_output_port(
            client, create_payload["data_product_id"], create_payload
        )
        assert created_dataset.status_code == 400

    def test_get_datasets(self, client):
        ds = OutputPortFactory()
        response = client.get(ENDPOINT.format(ds.data_product.id))
        assert response.status_code == 200
        data = response.json()["output_ports"]
        assert len(data) == 1
        assert data[0]["id"] == str(ds.id)

    def test_update_dataset_no_role(self, client):
        ds = OutputPortFactory()
        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tags": [],
            "access_type": "restricted",
        }

        updated_dataset = self.update_output_port(
            client, ds.data_product.id, ds.id, update_payload
        )

        assert updated_dataset.status_code == 403

    def test_update_dataset_type_public_renamed(self, session, client) -> None:
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tag_ids": [],
            "access_type": "public",
            "data_product_access_duration_type": AccessDurationType.TIME_BOUND.value,
            "exploration_access_duration_type": AccessDurationType.TIME_BOUND.value,
        }

        updated_dataset = self.update_output_port(
            client, ds.data_product.id, ds.id, update_payload
        )

        assert updated_dataset.status_code == 200
        dataset_id = updated_dataset.json()["id"]
        output_port: Dataset = session.query(Dataset).filter_by(id=dataset_id).first()
        assert output_port.access_type == OutputPortAccessType.UNRESTRICTED.value

    def test_update_dataset(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )

        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tag_ids": [],
            "access_type": "restricted",
            "data_product_access_duration_type": AccessDurationType.TIME_BOUND.value,
            "exploration_access_duration_type": AccessDurationType.TIME_BOUND.value,
        }

        updated_dataset = self.update_output_port(
            client, ds.data_product.id, ds.id, update_payload
        )

        assert updated_dataset.status_code == 200
        assert updated_dataset.json()["id"] == str(ds.id)

    def test_update_output_port(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )

        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tag_ids": [],
            "access_type": "restricted",
            "data_product_access_duration_type": AccessDurationType.TIME_BOUND.value,
            "exploration_access_duration_type": AccessDurationType.TIME_BOUND.value,
        }

        updated_dataset = self.update_output_port(
            client, ds.data_product.id, ds.id, update_payload
        )

        assert updated_dataset.status_code == 200
        assert updated_dataset.json()["id"] == str(ds.id)

    def test_update_dataset_about_no_role(self, client):
        ds = OutputPortFactory()
        response = self.update_output_port_about(client, ds.data_product.id, ds.id)
        assert response.status_code == 403

    def test_update_dataset_about(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        response = self.update_output_port_about(client, ds.data_product.id, ds.id)
        assert response.status_code == 200

    def test_update_output_port_about(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        response = self.update_output_port_about(client, ds.data_product.id, ds.id)
        assert response.status_code == 200

    def test_remove_dataset_not_owner(self, client):
        ds = OutputPortFactory()
        response = self.delete_output_port(client, ds.data_product.id, ds.id)
        assert response.status_code == 403

    def test_remove_dataset(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.OUTPUT_PORT__DELETE]
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        response = self.delete_output_port(client, ds.data_product.id, ds.id)
        assert response.status_code == 200

        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 404

    def test_remove_output_port(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.OUTPUT_PORT__DELETE]
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        response = self.delete_output_port(client, ds.data_product.id, ds.id)
        assert response.status_code == 200

        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 404

    def test_get_dataset_with_invalid_dataset_id(self, client):
        dp = DataProductFactory()
        dataset = self.get_output_port(client, dp.id, self.invalid_id)
        assert dataset.status_code == 404

    def test_get_dataset(
        self,
        client,
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.OUTPUT_PORT__DELETE]
        )
        data_product = DataProductFactory()
        data_output = TechnicalAssetFactory(owner=data_product)
        ds = OutputPortFactory(data_product=data_product)
        TechnicalAssetOutputPortAssociationFactory(
            output_port=ds, data_output=data_output
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        dataset = self.get_output_port(client, ds.id, data_product.id)
        assert dataset.status_code == 200

    def test_get_output_port(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.OUTPUT_PORT__DELETE]
        )
        data_product = DataProductFactory()
        data_output = TechnicalAssetFactory(owner=data_product)
        ds = OutputPortFactory(data_product=data_product)
        TechnicalAssetOutputPortAssociationFactory(
            output_port=ds, data_output=data_output
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        dataset = self.get_output_port(client, ds.id, ds.data_product.id)
        assert dataset.status_code == 200

    def test_update_dataset_with_invalid_dataset_id(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )

        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tags": [],
            "access_type": "public",
        }
        dataset = self.update_output_port(
            client, ds.data_product.id, self.invalid_id, update_payload
        )
        assert dataset.status_code == 403

    def test_remove_dataset_with_invalid_dataset_id(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.OUTPUT_PORT__DELETE]
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        dataset = self.delete_output_port(client, ds.data_product_id, self.invalid_id)
        assert dataset.status_code == 403

    def test_update_status_no_role(self, client):
        ds = OutputPortFactory()
        response = self.update_output_port_status(
            client, ds.data_product.id, ds.id, {"status": "active"}
        )
        assert response.status_code == 403

    def test_update_status(self, client):
        ds_owner = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_STATUS],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=ds_owner.id, role_id=role.id, output_port_id=ds.id
        )
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.json()["status"] == "active"
        response = self.update_output_port_status(
            client, ds.data_product.id, ds.id, {"status": "pending"}
        )
        assert response.status_code == 200
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.json()["status"] == "pending"

    def test_update_output_port_status(self, client):
        ds_owner = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_STATUS],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=ds_owner.id, role_id=role.id, output_port_id=ds.id
        )
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.json()["status"] == "active"
        response = self.update_output_port_status(
            client, ds.data_product.id, ds.id, {"status": "pending"}
        )
        assert response.status_code == 200
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.json()["status"] == "pending"

    def test_get_output_port_graph_data(self, client):
        dp = DataProductFactory()
        ds = OutputPortFactory(data_product=dp)
        response = client.get(f"{ENDPOINT.format(dp.id)}/{ds.id}/graph")
        assert response.json()["edges"] == [
            {
                "id": f"{str(dp.id)}-{str(ds.id)}-2",
                "source": f"{str(dp.id)}_2",
                "target": str(ds.id),
                "animated": True,
                "sourceHandle": "right_s",
                "targetHandle": "left_t",
            }
        ]
        nodes = response.json()["nodes"]
        dp_node = [node for node in nodes if node["type"] == "dataProductNode"][0]
        ds_node = [node for node in nodes if node["type"] == "outputPortNode"][0]
        assert dp_node == {
            "data": {
                "id": f"{str(dp.id)}",
                "name": dp.name,
                "description": None,
                "icon_key": "default",
                "domain": None,
                "domain_id": None,
                "link_to_id": None,
            },
            "id": f"{str(dp.id)}_2",
            "isMain": False,
            "type": "dataProductNode",
        }
        assert ds_node == {
            "data": {
                "icon_key": None,
                "id": str(ds.id),
                "link_to_id": str(dp.id),
                "name": ds.name,
                "domain": None,
                "domain_id": None,
                "description": None,
            },
            "id": str(ds.id),
            "isMain": True,
            "type": "outputPortNode",
        }

    def test_get_output_port_graph_data_exploration(self, client):
        ds = OutputPortFactory()
        exp = ExplorationFactory()
        InputPortFactory(
            output_port=ds,
            consuming_abstract_data_product=exp,
        )
        response = client.get(
            f"{ENDPOINT.format(ds.data_product.id)}/{ds.id}/graph", params={"level": 3}
        )
        assert response.status_code == 200, response.text

    def test_dataset_set_custom_setting_no_role(self, client):
        ds = OutputPortFactory()
        setting = DataProductSettingFactory(scope="dataset")
        response = client.post(
            f"{ENDPOINT.format(ds.data_product.id)}/{ds.id}/settings/{setting.id}"
        )
        assert response.status_code == 403

    def test_dataset_set_custom_setting(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_SETTINGS],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        setting = DataProductSettingFactory(scope="dataset")

        response = client.post(
            f"{ENDPOINT.format(ds.data_product.id)}/{ds.id}/settings/{setting.id}?value=false"
        )
        assert response.status_code == 200
        response = client.get(f"{ENDPOINT.format(ds.data_product.id)}/{ds.id}")
        assert response.json()["data_product_settings"][0]["value"] == "false"

    def test_output_port_set_custom_setting(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_SETTINGS],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        setting = DataProductSettingFactory(scope="dataset")

        response = client.post(
            f"{ENDPOINT.format(ds.data_product.id)}/{ds.id}/settings/{setting.id}?value=false"
        )
        assert response.status_code == 200
        response = client.get(f"{ENDPOINT.format(ds.data_product.id)}/{ds.id}")
        assert response.json()["data_product_settings"][0]["value"] == "false"

    def test_get_private_dataset_not_allowed(self, client):
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 403

    def test_get_private_dataset_by_owner(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory.dataset_owner()
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_get_private_dataset_by_admin(self, client):
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 200

    def test_get_private_dataset_by_member_of_consuming_data_product(self, client):
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        dp = DataProductFactory()
        InputPortFactory(consuming_abstract_data_product=dp, output_port=ds)
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            data_product_id=dp.id, user_id=user.id, role_id=role.id
        )

        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 200, response.text

    def test_get_private_datasets_not_allowed(self, client):
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        response = client.get(ENDPOINT.format(ds.data_product.id))
        assert response.status_code == 200
        assert len(response.json()["output_ports"]) == 0

    def test_get_private_datasets_by_owner(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory.data_product_owner()
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        response = client.get(ENDPOINT.format(ds.data_product.id))
        assert response.status_code == 200
        assert len(response.json()["output_ports"]) == 1

    @pytest.mark.usefixtures("admin")
    def test_get_private_datasets_by_admin(self, client):
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        response = client.get(ENDPOINT.format(ds.data_product.id))
        assert response.status_code == 200
        assert len(response.json()["output_ports"]) == 1

    def test_get_private_datasets_by_member_of_consuming_data_product(self, client):
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        dp = DataProductFactory()
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=dp.id
        )
        InputPortFactory(consuming_abstract_data_product=dp, output_port=ds)

        response = client.get(ENDPOINT.format(ds.data_product_id))
        assert response.status_code == 200
        assert len(response.json()["output_ports"]) == 1

    def test_validate_namespace(self, client):
        namespace = "test"
        response = self.validate_namespace(client, namespace)

        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.VALID.value

    def test_validate_namespace_invalid_characters(self, client):
        namespace = "!"
        response = self.validate_namespace(client, namespace)
        assert response.status_code == 200
        assert (
            response.json()["validity"]
            == ResourceNameValidityType.INVALID_CHARACTERS.value
        )

    def test_validate_namespace_invalid_length(self, client):
        namespace = "a" * 256
        response = self.validate_namespace(client, namespace)
        assert response.status_code == 200
        assert (
            response.json()["validity"] == ResourceNameValidityType.INVALID_LENGTH.value
        )

    def test_validate_namespace_duplicate(self, client):
        namespace = "test"
        OutputPortFactory(namespace=namespace)
        response = self.validate_namespace(client, namespace)
        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.DUPLICATE.value

    def test_update_dataset_duplicate_namespace(self, client):
        namespace = "namespace"
        OutputPortFactory(namespace=namespace)
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        update_payload = {
            "name": "new_name",
            "namespace": namespace,
            "description": "new_description",
            "tag_ids": [],
            "access_type": "public",
            "data_product_access_duration_type": AccessDurationType.TIME_BOUND.value,
            "exploration_access_duration_type": AccessDurationType.TIME_BOUND.value,
        }

        response = self.update_output_port(
            client, ds.data_product.id, ds.id, update_payload
        )

        assert response.status_code == 400

    def test_history_event_created_on_create_dataset(self, dataset_payload, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        created_dataset = self.create_output_port(
            client, dataset_payload["data_product_id"], dataset_payload
        )
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

        history = self.get_output_port_history(
            client,
            created_dataset.json().get("id"),
            dataset_payload.get("data_product_id"),
        )
        assert len(history.json()["events"]) == 2

    def test_get_output_port_history(self, dataset_payload, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        created_dataset = self.create_output_port(
            client, dataset_payload["data_product_id"], dataset_payload
        )
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

        history = self.get_output_port_history(
            client,
            created_dataset.json().get("id"),
            dataset_payload.get("data_product_id"),
        )
        assert history.status_code == 200
        assert len(history.json()["events"]) == 2

    def test_history_event_created_on_update_dataset(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )

        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tag_ids": [],
            "access_type": "public",
            "data_product_access_duration_type": AccessDurationType.TIME_BOUND.value,
            "exploration_access_duration_type": AccessDurationType.TIME_BOUND.value,
        }

        updated_dataset = self.update_output_port(
            client, ds.data_product.id, ds.id, update_payload
        )
        assert updated_dataset.status_code == 200

        history = self.get_output_port_history(client, ds.id, ds.data_product.id)
        assert len(history.json()["events"]) == 1

    def test_history_event_created_on_update_about_dataset(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        response = self.update_output_port_about(client, ds.data_product.id, ds.id)
        assert response.status_code == 200

        history = self.get_output_port_history(client, ds.id, ds.data_product.id)
        assert len(history.json()["events"]) == 1

    def test_history_event_created_on_update_status_dataset(self, client):
        ds_owner = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_STATUS],
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=ds_owner.id, role_id=role.id, output_port_id=ds.id
        )
        response = self.update_output_port_status(
            client, ds.data_product.id, ds.id, {"status": "pending"}
        )
        assert response.status_code == 200

        history = self.get_output_port_history(client, ds.id, ds.data_product.id)
        assert len(history.json()["events"]) == 1

    def test_history_event_created_on_removing_dataset(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.OUTPUT_PORT__DELETE]
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        response = self.delete_output_port(client, ds.data_product_id, ds.id)
        assert response.status_code == 200

        history = self.get_output_port_history(client, ds.id, ds.data_product.id)
        assert history.status_code == 404

        events = EventService(db=test_session).get_history(
            ds.data_product_id, EventReferenceEntity.DATA_PRODUCT
        )
        assert len(events) == 1
        assert events[0].deleted_subject_identifier == ds.name

    def test_retain_deleted_dataset_name_in_history(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.OUTPUT_PORT__DELETE]
        )
        ds = OutputPortFactory()
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        dataset_id = ds.id
        dataset_name = ds.name

        response = self.delete_output_port(client, ds.data_product_id, ds.id)
        assert response.status_code == 200

        events = EventService(db=test_session).get_history(
            dataset_id, EventReferenceEntity.DATASET
        )
        assert len(events) == 1
        assert events[0].deleted_subject_identifier == dataset_name

    def test_create_generates_webhook_v2_event(
        self, mock_webhook, dataset_payload, client
    ):
        self.test_create_dataset(dataset_payload, client)
        assert_event_in_queue("output_port.event", mock_webhook)

    @staticmethod
    def create_output_port(client, data_product_id, output_port_payload):
        return client.post(ENDPOINT.format(data_product_id), json=output_port_payload)

    @staticmethod
    def update_output_port_status(client, data_product_id, dataset_id, status):
        return client.put(
            f"{ENDPOINT.format(data_product_id)}/{dataset_id}/status", json=status
        )

    @staticmethod
    def update_output_port(client, data_product_id, dataset_id, payload):
        return client.put(
            f"{ENDPOINT.format(data_product_id)}/{dataset_id}", json=payload
        )

    @staticmethod
    def update_output_port_about(client, data_product_id, output_port_id, payload=None):
        if payload is None:
            payload = {"about": "Updated Dataset Description"}
        return client.put(
            f"{ENDPOINT.format(data_product_id)}/{output_port_id}/about", json=payload
        )

    @staticmethod
    def delete_output_port(client, data_product_id, dataset_id):
        return client.delete(f"{ENDPOINT.format(data_product_id)}/{dataset_id}")

    @staticmethod
    def get_output_port(client, dataset_id, data_product_id):
        return client.get(f"{ENDPOINT.format(data_product_id)}/{dataset_id}")

    @staticmethod
    def validate_namespace(client, namespace):
        return client.get(
            "api/v2/resource_names/validate",
            params={"resource_name": namespace, "model": "output_port"},
        )

    @staticmethod
    def get_output_port_history(client, output_port_id, data_product_id):
        return client.get(
            f"{ENDPOINT.format(data_product_id)}/{output_port_id}/history"
        )

    @staticmethod
    def _op_endpoint(dp_id):
        return ENDPOINT.format(dp_id)

    @staticmethod
    def get_access_durations(client, data_product_id, output_port_id):
        return client.get(
            f"{ENDPOINT.format(data_product_id)}/{output_port_id}/access_durations"
        )

    def test_both_permanent(self, client):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory(
            data_product_access_duration_type=AccessDurationType.PERMANENT,
            exploration_access_duration_type=AccessDurationType.PERMANENT,
        )

        response = self.get_access_durations(client, ds.data_product_id, ds.id)

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["data_product_access_duration"] == {
            "access_duration_type": "permanent",
            "days": -1,
        }
        assert body["exploration_access_duration"] == {
            "access_duration_type": "permanent",
            "days": -1,
        }

    def test_time_bound_returns_configured_days(self, client):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
        )
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.EXPLORATION,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=14,
        )
        ds = OutputPortFactory(
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
            exploration_access_duration_type=AccessDurationType.TIME_BOUND,
        )

        response = self.get_access_durations(client, ds.data_product_id, ds.id)

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["data_product_access_duration"] == {
            "access_duration_type": "time_bound",
            "days": 30,
        }
        assert body["exploration_access_duration"] == {
            "access_duration_type": "time_bound",
            "days": 14,
        }

    def test_private_dataset_forbidden_for_non_member(self, client):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)

        response = self.get_access_durations(client, ds.data_product_id, ds.id)

        assert response.status_code == 403

    def test_unknown_output_port_returns_404(self, client):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        dp = DataProductFactory()

        response = self.get_access_durations(client, dp.id, uuid4())

        assert response.status_code == 404

    def test_wrong_data_product_id_returns_404(self, client):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory()
        other_dp = DataProductFactory()

        response = self.get_access_durations(client, other_dp.id, ds.id)

        assert response.status_code == 404
