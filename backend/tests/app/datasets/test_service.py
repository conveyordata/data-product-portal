from sqlalchemy.orm import joinedload
from tests import test_session
from tests.factories import (
    DataProductDatasetAssociationFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    GlobalRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

from app.datasets.enums import DatasetAccessType
from app.datasets.model import Dataset
from app.datasets.service import DatasetService
from app.roles import ADMIN_UUID
from app.roles.schema import Prototype, Scope


class TestDatasetsService:
    def test_private_dataset_not_visible(self):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        ds = self.get_dataset(ds)
        assert DatasetService(test_session).is_visible_to_user(ds, user) is False

    def test_get_private_dataset_by_owner(self):
        owner = UserFactory(external_id="sub")
        role = RoleFactory(scope=Scope.DATASET, prototype=Prototype.OWNER)
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        DatasetRoleAssignmentFactory(
            role_id=role.id, dataset_id=ds.id, user_id=owner.id
        )
        ds = self.get_dataset(ds)
        assert DatasetService(test_session).is_visible_to_user(ds, owner) is True

    def test_get_private_dataset_by_admin(self):
        admin = UserFactory(external_id="sub")
        role = RoleFactory(scope=Scope.GLOBAL, prototype=Prototype.ADMIN, id=ADMIN_UUID)
        GlobalRoleAssignmentFactory(role_id=role.id, user_id=admin.id)
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        ds = self.get_dataset(ds)
        assert DatasetService(test_session).is_visible_to_user(ds, admin) is True

    def test_get_private_dataset_by_member_of_consuming_data_product(self):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        dp = DataProductFactory()
        role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            role_id=role.id, data_product_id=dp.id, user_id=user.id
        )
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)
        ds = self.get_dataset(ds)
        assert DatasetService(test_session).is_visible_to_user(ds, user) is True

    @staticmethod
    def get_dataset(dataset: Dataset) -> Dataset:
        return test_session.get(
            Dataset,
            dataset.id,
            options=[joinedload(Dataset.data_product_links)],
            populate_existing=True,
        )
