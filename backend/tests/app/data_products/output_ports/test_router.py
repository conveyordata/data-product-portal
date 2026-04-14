from copy import deepcopy

import pytest

from app.authorization.roles.schema import Prototype, Scope
from app.authorization.roles.service import RoleService
from app.core.authz.actions import AuthorizationAction
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import Dataset
from app.events.enums import EventReferenceEntity
from app.events.service import EventService
from app.resource_names.service import ResourceNameValidityType
from app.settings import settings
from tests import test_session
from tests.factories import (
    DataOutputDatasetAssociationFactory,
    DataProductDatasetAssociationFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DataProductSettingFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    DomainFactory,
    GlobalRoleAssignmentFactory,
    RoleFactory,
    TechnicalAssetFactory,
    UserFactory,
)

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
    }


class TestDatasetsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_create_dataset(self, session, dataset_payload, client):
        RoleService(db=session).initialize_prototype_roles()
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

    def test_create_output_port(self, session, dataset_payload, client):
        RoleService(db=session).initialize_prototype_roles()
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

    def test_create_output_port_type_public(self, session, dataset_payload, client):
        RoleService(db=session).initialize_prototype_roles()
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

    def test_create_dataset_no_owner_role(self, dataset_payload, client):
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
        assert created_dataset.status_code == 400

    def test_create_dataset_no_owners(self, session, dataset_payload, client):
        RoleService(db=session).initialize_prototype_roles()
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
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        DatasetFactory(namespace=dataset_payload["namespace"])

        created_dataset = self.create_output_port(
            client, dataset_payload["data_product_id"], dataset_payload
        )
        assert created_dataset.status_code == 400

    def test_create_dataset_invalid_characters_namespace(
        self, session, dataset_payload, client
    ):
        RoleService(db=session).initialize_prototype_roles()
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
        RoleService(db=session).initialize_prototype_roles()
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
        ds = DatasetFactory()
        response = client.get(ENDPOINT.format(ds.data_product.id))
        assert response.status_code == 200
        data = response.json()["output_ports"]
        assert len(data) == 1
        assert data[0]["id"] == str(ds.id)

    def test_update_dataset_no_role(self, client):
        ds = DatasetFactory()
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

    def test_update_dataset_type_public_renamed(self, session, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tag_ids": [],
            "access_type": "public",
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tag_ids": [],
            "access_type": "restricted",
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tag_ids": [],
            "access_type": "restricted",
        }

        updated_dataset = self.update_output_port(
            client, ds.data_product.id, ds.id, update_payload
        )

        assert updated_dataset.status_code == 200
        assert updated_dataset.json()["id"] == str(ds.id)

    def test_update_dataset_about_no_role(self, client):
        ds = DatasetFactory()
        response = self.update_output_port_about(client, ds.data_product.id, ds.id)
        assert response.status_code == 403

    def test_update_dataset_about(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        response = self.update_output_port_about(client, ds.data_product.id, ds.id)
        assert response.status_code == 200

    def test_update_output_port_about(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        response = self.update_output_port_about(client, ds.data_product.id, ds.id)
        assert response.status_code == 200

    def test_remove_dataset_not_owner(self, client):
        ds = DatasetFactory()
        response = self.delete_output_port(client, ds.data_product.id, ds.id)
        assert response.status_code == 403

    def test_remove_dataset(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.OUTPUT_PORT__DELETE]
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        response = self.delete_output_port(client, ds.data_product.id, ds.id)
        assert response.status_code == 200

        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 404

    def test_remove_output_port(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.OUTPUT_PORT__DELETE]
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
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
        ds = DatasetFactory(data_product=data_product)
        DataOutputDatasetAssociationFactory(dataset=ds, data_output=data_output)
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        dataset = self.get_output_port(client, ds.id, data_product.id)
        assert dataset.status_code == 200

    def test_get_output_port(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.OUTPUT_PORT__DELETE]
        )
        data_product = DataProductFactory()
        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory(data_product=data_product)
        DataOutputDatasetAssociationFactory(dataset=ds, data_output=data_output)
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        dataset = self.get_output_port(client, ds.id, ds.data_product.id)
        assert dataset.status_code == 200

    def test_update_dataset_with_invalid_dataset_id(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        dataset = self.delete_output_port(client, ds.data_product_id, self.invalid_id)
        assert dataset.status_code == 403

    def test_update_status_no_role(self, client):
        ds = DatasetFactory()
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(
            user_id=ds_owner.id, role_id=role.id, dataset_id=ds.id
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(
            user_id=ds_owner.id, role_id=role.id, dataset_id=ds.id
        )
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.json()["status"] == "active"
        response = self.update_output_port_status(
            client, ds.data_product.id, ds.id, {"status": "pending"}
        )
        assert response.status_code == 200
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.json()["status"] == "pending"

    def test_get_graph_data(self, client):
        dp = DataProductFactory()
        ds = DatasetFactory(data_product=dp)
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
        ds_node = [node for node in nodes if node["type"] == "datasetNode"][0]
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
            "type": "datasetNode",
        }

    def test_dataset_set_custom_setting_no_role(self, client):
        ds = DatasetFactory()
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        setting = DataProductSettingFactory(scope="dataset")

        response = client.post(
            f"{ENDPOINT.format(ds.data_product.id)}/{ds.id}/settings/{setting.id}?value=false"
        )
        assert response.status_code == 200
        response = client.get(f"{ENDPOINT.format(ds.data_product.id)}/{ds.id}")
        assert response.json()["data_product_settings"][0]["value"] == "false"

    def test_get_private_dataset_not_allowed(self, client):
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 403

    def test_get_private_dataset_by_owner(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.DATASET, prototype=Prototype.OWNER)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_get_private_dataset_by_admin(self, client):
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 200

    def test_get_private_dataset_by_member_of_consuming_data_product(self, client):
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        dp = DataProductFactory()
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            data_product_id=dp.id, user_id=user.id, role_id=role.id
        )

        response = self.get_output_port(client, ds.id, ds.data_product.id)
        assert response.status_code == 200

    def test_get_private_datasets_not_allowed(self, client):
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        response = client.get(ENDPOINT.format(ds.data_product.id))
        assert response.status_code == 200
        # TODO This logic needs to be checked!
        assert len(response.json()["output_ports"]) == 1

    def test_get_private_datasets_by_owner(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.DATA_PRODUCT, prototype=Prototype.OWNER)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        response = client.get(ENDPOINT.format(ds.data_product.id))
        assert response.status_code == 200
        assert len(response.json()["output_ports"]) == 1

    @pytest.mark.usefixtures("admin")
    def test_get_private_datasets_by_admin(self, client):
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        response = client.get(ENDPOINT.format(ds.data_product.id))
        assert response.status_code == 200
        assert len(response.json()["output_ports"]) == 1

    def test_get_private_datasets_by_member_of_consuming_data_product(self, client):
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        dp = DataProductFactory()
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=dp.id
        )
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)

        response = client.get(ENDPOINT.format(dp.id))
        assert response.status_code == 200
        # TODO This logic needs to be checked
        assert len(response.json()["output_ports"]) == 0

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
        DatasetFactory(namespace=namespace)
        response = self.validate_namespace(client, namespace)
        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.DUPLICATE.value

    def test_update_dataset_duplicate_namespace(self, client):
        namespace = "namespace"
        DatasetFactory(namespace=namespace)
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        update_payload = {
            "name": "new_name",
            "namespace": namespace,
            "description": "new_description",
            "tag_ids": [],
            "access_type": "public",
        }

        response = self.update_output_port(
            client, ds.data_product.id, ds.id, update_payload
        )

        assert response.status_code == 400

    def test_history_event_created_on_create_dataset(
        self, session, dataset_payload, client
    ):
        RoleService(db=session).initialize_prototype_roles()
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

    def test_get_output_port_history(self, session, dataset_payload, client):
        RoleService(db=session).initialize_prototype_roles()
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tag_ids": [],
            "access_type": "public",
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(
            user_id=ds_owner.id, role_id=role.id, dataset_id=ds.id
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
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
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        dataset_id = ds.id
        dataset_name = ds.name

        response = self.delete_output_port(client, ds.data_product_id, ds.id)
        assert response.status_code == 200

        events = EventService(db=test_session).get_history(
            dataset_id, EventReferenceEntity.DATASET
        )
        assert len(events) == 1
        assert events[0].deleted_subject_identifier == dataset_name

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
