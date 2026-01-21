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
    DataOutputFactory,
    DataProductDatasetAssociationFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    GlobalRoleAssignmentFactory,
    RoleFactory,
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

    def test_recalculate_embedding(self):
        ds = DatasetFactory()
        OutputPortService(test_session).recalculate_embedding(ds.id)

    def test_recalculate_embedding_with_technical_asset(self):
        ds = DatasetFactory()
        data_output = DataOutputFactory(owner=ds.data_product)
        DataOutputDatasetAssociationFactory(data_output=data_output, dataset=ds)
        OutputPortService(test_session).recalculate_embedding(ds.id)

    def test_recalculate_all_embeddings(self):
        for i in range(51):  # Ensure we load 2 batches
            DatasetFactory()
        OutputPortService(test_session).recalculate_all_embeddings()

    @staticmethod
    def get_dataset(dataset: Dataset) -> Dataset:
        return test_session.get(
            Dataset,
            dataset.id,
            options=[selectinload(Dataset.data_product_links)],
            populate_existing=True,
        )
