from sqlalchemy.orm import joinedload
from tests import test_session
from tests.factories import (
    DataProductDatasetAssociationFactory,
    DataProductMembershipFactory,
    DatasetFactory,
    UserFactory,
)

from app.datasets.enums import DatasetAccessType
from app.datasets.model import Dataset


class TestDatasetsModel:
    def test_private_dataset_not_visible(self):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        ds = self.get_dataset(ds)
        assert ds.isVisibleToUser(user) is False

    def test_get_private_dataset_by_owner(self, client):
        ds_owner = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE, owners=[ds_owner])
        ds = self.get_dataset(ds)
        assert ds.isVisibleToUser(ds_owner) is True

    def test_get_private_dataset_by_admin(self, client):
        admin = UserFactory(external_id="sub", is_admin=True)
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        ds = self.get_dataset(ds)
        assert ds.isVisibleToUser(admin) is True

    def test_get_private_dataset_by_member_of_consuming_data_product(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        dp = DataProductMembershipFactory(user=user).data_product
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)
        ds = self.get_dataset(ds)
        assert ds.isVisibleToUser(user) is True

    @staticmethod
    def get_dataset(dataset: Dataset) -> Dataset:
        return test_session.get(
            Dataset,
            dataset.id,
            options=[joinedload(Dataset.data_product_links)],
            populate_existing=True,
        )
