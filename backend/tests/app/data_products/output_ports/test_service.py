from sqlalchemy.orm import selectinload

from app.authorization.roles import ADMIN_UUID
from app.authorization.roles.schema import Prototype, Scope
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import Dataset
from app.data_products.output_ports.service import OutputPortService
from app.settings import settings
from tests import test_session
from tests.factories import (
    DataOutputDatasetAssociationFactory,
    DataProductDatasetAssociationFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    GlobalRoleAssignmentFactory,
    RoleFactory,
    TechnicalAssetFactory,
    UserFactory,
)


class TestDatasetsService:
    def test_private_dataset_not_visible(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        ds = self.get_dataset(ds)
        assert OutputPortService(test_session).is_visible_to_user(ds, user) is False

    def test_get_private_dataset_by_owner(self):
        owner = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.DATASET, prototype=Prototype.OWNER)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        DatasetRoleAssignmentFactory(
            role_id=role.id, dataset_id=ds.id, user_id=owner.id
        )
        ds = self.get_dataset(ds)
        assert OutputPortService(test_session).is_visible_to_user(ds, owner) is True

    def test_get_private_dataset_by_admin(self):
        admin = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.GLOBAL, prototype=Prototype.ADMIN, id=ADMIN_UUID)
        GlobalRoleAssignmentFactory(role_id=role.id, user_id=admin.id)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        ds = self.get_dataset(ds)
        assert OutputPortService(test_session).is_visible_to_user(ds, admin) is True

    def test_get_private_dataset_by_member_of_consuming_data_product(self):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        dp = DataProductFactory()
        role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            role_id=role.id, data_product_id=dp.id, user_id=user.id
        )
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)
        ds = self.get_dataset(ds)
        assert OutputPortService(test_session).is_visible_to_user(ds, user) is True

    def test_recalculate_search(self):
        ds = DatasetFactory()
        OutputPortService(test_session).recalculate_search(ds.id)

    def test_recalculate_search_with_technical_asset(self):
        ds = DatasetFactory()
        data_output = TechnicalAssetFactory(owner=ds.data_product)
        DataOutputDatasetAssociationFactory(data_output=data_output, dataset=ds)
        OutputPortService(test_session).recalculate_search(ds.id)

    def test_recalculate_search_for_all_output_ports(self):
        for i in range(51):  # Ensure we load 2 batches
            DatasetFactory()
        OutputPortService(test_session).recalculate_search_for_all_output_ports()

    def test_search_output_ports_excludes_private_datasets(self):
        """Test that private output ports are not visible in search results to unauthorized users"""
        # Create a regular user without special permissions
        regular_user = UserFactory(external_id=settings.DEFAULT_USERNAME)

        # Create a public output port that should be visible
        public_dataset = DatasetFactory(
            name="Public Analytics Dataset", access_type=OutputPortAccessType.PUBLIC
        )

        # Create a private output port that should NOT be visible
        private_dataset = DatasetFactory(
            name="Private Sensitive Dataset", access_type=OutputPortAccessType.PRIVATE
        )

        # Create another private output port owned by a different user
        owner = UserFactory()
        owner_role = RoleFactory(scope=Scope.DATASET, prototype=Prototype.OWNER)
        owned_private_dataset = DatasetFactory(
            name="Owner Private Dataset", access_type=OutputPortAccessType.PRIVATE
        )
        DatasetRoleAssignmentFactory(
            role_id=owner_role.id, dataset_id=owned_private_dataset.id, user_id=owner.id
        )

        # Recalculate search embeddings for all datasets
        OutputPortService(test_session).recalculate_search(public_dataset.id)
        OutputPortService(test_session).recalculate_search(private_dataset.id)
        OutputPortService(test_session).recalculate_search(owned_private_dataset.id)

        # Search as the regular user
        search_results = OutputPortService(test_session).search_datasets(
            query=None, limit=100, user=regular_user, current_user_assigned=False
        )

        # Extract dataset IDs from results
        result_ids = [ds.id for ds in search_results]

        # Assert that public dataset is visible
        assert public_dataset.id in result_ids, (
            "Public dataset should be visible to all users"
        )

        # Assert that private datasets are NOT visible
        assert private_dataset.id not in result_ids, (
            "Private dataset should not be visible to unauthorized users"
        )
        assert owned_private_dataset.id not in result_ids, (
            "Owner's private dataset should not be visible to other users"
        )

    def test_search_output_ports_owner_can_see_own_private_datasets(self):
        """Test that owners can see their own private output ports in search results"""
        # Create a user who will own a private dataset
        owner = UserFactory(external_id=settings.DEFAULT_USERNAME)
        owner_role = RoleFactory(scope=Scope.DATASET, prototype=Prototype.OWNER)

        # Create a private output port owned by this user
        private_dataset = DatasetFactory(
            name="My Private Dataset", access_type=OutputPortAccessType.PRIVATE
        )
        DatasetRoleAssignmentFactory(
            role_id=owner_role.id, dataset_id=private_dataset.id, user_id=owner.id
        )

        # Create a public dataset for comparison
        public_dataset = DatasetFactory(
            name="Public Dataset", access_type=OutputPortAccessType.PUBLIC
        )

        # Recalculate search embeddings
        OutputPortService(test_session).recalculate_search(private_dataset.id)
        OutputPortService(test_session).recalculate_search(public_dataset.id)

        # Search as the owner
        search_results = OutputPortService(test_session).search_datasets(
            query=None, limit=100, user=owner, current_user_assigned=False
        )

        # Extract dataset IDs from results
        result_ids = [ds.id for ds in search_results]

        # Assert that both datasets are visible to the owner
        assert private_dataset.id in result_ids, (
            "Owner should see their own private dataset"
        )
        assert public_dataset.id in result_ids, "Owner should also see public datasets"

    @staticmethod
    def get_dataset(dataset: Dataset) -> Dataset:
        return test_session.get(
            Dataset,
            dataset.id,
            options=[selectinload(Dataset.data_product_links)],
            populate_existing=True,
        )
