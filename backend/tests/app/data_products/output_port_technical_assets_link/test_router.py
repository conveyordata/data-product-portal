import pytest

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.output_ports.enums import OutputPortAccessType
from app.settings import settings
from tests.factories import (
    DataOutputDatasetAssociationFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    RoleFactory,
    TechnicalAssetFactory,
    UserFactory,
)

DATA_OUTPUTS_DATASETS_ENDPOINT = (
    "api/v2/data_products/{}/output_ports/{}/technical_assets"
)


class TestOutputPortsTechnicalAssetsLinkRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_request_data_output_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory(data_product=data_product)

        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 200

    def test_request_data_output_new(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory(data_product=data_product)

        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 200

    def test_request_data_output_link_on_dataset_with_diff_parent(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory()

        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 404

    def test_request_already_exists(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory(data_product=data_product)

        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 200
        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 400

    def test_request_data_output_link_private_dataset_no_access(self, client):
        data_product = DataProductFactory()
        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)

        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 403

    def test_request_data_output_link_private_dataset(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory(
            access_type=OutputPortAccessType.PRIVATE, data_product=data_product
        )
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 200

    def test_request_data_output_remove(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory(data_product=data_product)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK,
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
            ],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )

        assert response.status_code == 200

        response = self.request_data_output_dataset_unlink_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 200

    def test_request_data_output_remove_new(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory(data_product=data_product)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK,
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
            ],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )

        assert response.status_code == 200

        response = self.request_data_output_dataset_unlink_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_request_data_output_link_by_admin(self, client):
        data_product = DataProductFactory()
        data_output = TechnicalAssetFactory(owner=data_product)

        ds = DatasetFactory(data_product=data_product)

        link = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert link.status_code == 200

    def test_approve_data_output_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.approve_link_between_technical_asset_and_output_port(
            client, ds.data_product.id, link.data_output.id, link.dataset.id
        )
        assert response.status_code == 200, response.text

    def test_approve_link_between_technical_asset_and_output_port(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.approve_link_between_technical_asset_and_output_port(
            client, ds.data_product.id, link.data_output.id, link.dataset.id
        )
        assert response.status_code == 200, response.text

    @pytest.mark.usefixtures("admin")
    def test_approve_data_output_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.approve_link_between_technical_asset_and_output_port(
            client, ds.data_product.id, link.data_output.id, link.dataset.id
        )
        assert response.status_code == 200

    def test_not_owner_cannot_approved_link(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.approve_link_between_technical_asset_and_output_port(
            client, ds.data_product.id, link.data_output.id, link.dataset.id
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You don't have permission to perform this action"
        )

    def test_deny_data_output_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.deny_link_between_technical_asset_and_output_port(
            client, ds.data_product.id, link.data_output.id, link.dataset.id
        )
        assert response.status_code == 200

    def test_deny_link_between_technical_asset_and_output_port(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.deny_link_between_technical_asset_and_output_port(
            client, ds.data_product.id, link.data_output.id, link.dataset.id
        )
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_deny_data_output_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.deny_link_between_technical_asset_and_output_port(
            client, ds.data_product.id, link.data_output.id, link.dataset.id
        )
        assert response.status_code == 200

    def test_not_owner_cannot_deny_link(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.deny_link_between_technical_asset_and_output_port(
            client, ds.data_product.id, link.data_output.id, link.dataset.id
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You don't have permission to perform this action"
        )

    def test_remove_data_output_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=ds.data_product.id
        )
        data_output = TechnicalAssetFactory(owner=ds.data_product)
        DataOutputDatasetAssociationFactory(dataset=ds, data_output=data_output)

        response = self.request_data_output_dataset_unlink_new(
            client, ds.data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 200, response.text

    @pytest.mark.usefixtures("admin")
    def test_remove_data_output_link_by_admin(self, client):
        ds = DatasetFactory()
        data_output = TechnicalAssetFactory(owner=ds.data_product)
        DataOutputDatasetAssociationFactory(dataset=ds, data_output=data_output)

        response = self.request_data_output_dataset_unlink_new(
            client, ds.data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 200

    def test_request_dataset_link_with_invalid_dataset_id(self, client):
        data_product = DataProductFactory()
        data_output = TechnicalAssetFactory(owner=data_product)
        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, self.invalid_id
        )
        assert response.status_code == 403

    def test_delete_dataset_with_data_output_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[Action.OUTPUT_PORT__DELETE]
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataOutputDatasetAssociationFactory(dataset=ds)
        response = client.get(
            f"/api/v2/data_products/{link.data_output.owner.id}/technical_assets"
        )
        assert response.json()["technical_assets"][0]["output_port_links"][0][
            "output_port_id"
        ] == str(ds.id)
        response = client.delete(
            f"/api/v2/data_products/{ds.data_product.id}/output_ports/{ds.id}"
        )
        assert response.status_code == 200
        response = client.get(
            f"/api/v2/data_products/{link.data_output.owner.id}/technical_assets"
        )
        assert len(response.json()["technical_assets"][0]["output_port_links"]) == 0

    def test_history_event_created_on_request_data_output_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory(data_product=data_product)

        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 200

        response = self.get_data_output_history(
            client, data_product.id, data_output.id
        )
        assert 200 == response.status_code, response.text
        assert len(response.json()["events"]) == 1

    def test_history_event_created_on_remove_data_output_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=ds.data_product.id
        )
        technical_asset = TechnicalAssetFactory(owner=ds.data_product)
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, data_output=technical_asset
        )
        owner_id = link.data_output.owner.id
        output_id = link.data_output.id

        response = self.request_data_output_dataset_unlink_new(
            client, ds.data_product.id, technical_asset.id, ds.id
        )
        assert response.status_code == 200

        history = self.get_data_output_history(client, owner_id, output_id).json()
        assert len(history["events"]) == 1

    def test_history_event_created_on_approve_data_output_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.approve_link_between_technical_asset_and_output_port(
            client, ds.data_product.id, link.data_output.id, ds.id
        )
        assert response.status_code == 200

        history = self.get_data_output_history(
            client, link.data_output.owner.id, link.data_output.id
        ).json()
        assert len(history["events"]) == 1

    def test_history_event_created_on_deny_data_output_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.deny_link_between_technical_asset_and_output_port(
            client, ds.data_product.id, link.data_output.id, ds.id
        )
        assert response.status_code == 200

        history = self.get_data_output_history(
            client, link.data_output.owner.id, link.data_output.id
        ).json()
        assert len(history["events"]) == 1

    def test_history_event_created_on_unlink_data_output_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        data_output = TechnicalAssetFactory(owner=data_product)
        ds = DatasetFactory(data_product=data_product)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK,
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
            ],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        response = self.request_data_output_dataset_link_new(
            client, data_product.id, data_output.id, ds.id
        )

        assert response.status_code == 200

        response = self.request_data_output_dataset_unlink_new(
            client, data_product.id, data_output.id, ds.id
        )
        assert response.status_code == 200

        history = self.get_data_output_history(
            client, data_product.id, data_output.id
        ).json()
        assert len(history["events"]) == 2

    @staticmethod
    def request_data_output_dataset_link_new(
        client, data_product_id, technical_asset_id, output_port_id
    ):
        return client.post(
            f"{DATA_OUTPUTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/add",
            json={"technical_asset_id": f"{technical_asset_id}"},
        )

    @staticmethod
    def approve_link_between_technical_asset_and_output_port(
        client, data_product_id, technical_asset_id, output_port_id
    ):
        return client.post(
            f"{DATA_OUTPUTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/approve_link_request",
            json={"technical_asset_id": f"{technical_asset_id}"},
        )

    @staticmethod
    def deny_link_between_technical_asset_and_output_port(
        client, data_product_id, technical_asset_id, output_port_id
    ):
        return client.post(
            f"{DATA_OUTPUTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/deny_link_request",
            json={"technical_asset_id": f"{technical_asset_id}"},
        )

    @staticmethod
    def request_data_output_dataset_unlink_new(
        client, data_product_id, technical_asset_id, output_port_id
    ):
        return client.request(
            method="DELETE",
            url=f"{DATA_OUTPUTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/remove",
            json={"technical_asset_id": f"{technical_asset_id}"},
        )

    @staticmethod
    def get_data_output_history(client, data_product_id, data_output_id):
        return client.get(
            f"/api/v2/data_products/{data_product_id}/technical_assets/{data_output_id}/history"
        )
