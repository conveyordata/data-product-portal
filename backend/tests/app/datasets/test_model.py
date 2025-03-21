from tests.factories import (
    DataProductDatasetAssociationFactory,
    DataProductMembershipFactory,
    DatasetFactory,
    UserFactory,
)

from app.datasets.enums import DatasetAccessType


class TestDatasetsModel:
    def test_private_dataset_not_visible(self):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        assert ds.isVisibleToUser(user) is False

    def test_get_private_dataset_by_owner(self, client):
        ds_owner = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE, owners=[ds_owner])
        assert ds.isVisibleToUser(ds_owner) is True

    def test_get_private_dataset_by_admin(self, client):
        admin = UserFactory(external_id="sub", is_admin=True)
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        assert ds.isVisibleToUser(admin) is True

    def test_get_private_dataset_by_member_of_consuming_data_product(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        dp = DataProductMembershipFactory(user=user).data_product
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)
        assert ds.isVisibleToUser(user) is True
