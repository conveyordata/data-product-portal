import pytest

from tests.factories import (
    DataProductDatasetAssociationFactory,
    DataProductFactory,
    DatasetFactory,
    TechnicalAssetFactory,
)

OLD_ENDPOINT = "/api/graph"
ENDPOINT = "/api/v2/graph"


class TestGraphRouter:
    @pytest.mark.parametrize(
        "route",
        [
            OLD_ENDPOINT,
            ENDPOINT,
        ],
    )
    def test_get_graph_data(self, client, route):
        data_product = DataProductFactory()
        DatasetFactory(data_product=data_product)
        TechnicalAssetFactory(owner=data_product)
        response = client.get(route)
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 1
        assert len(response.json()["nodes"]) == 2

    def test_get_graph_data_1_link(self, client):
        data_product_1 = DataProductFactory()
        dataset = DatasetFactory(data_product=data_product_1)
        data_product_2 = DataProductFactory()
        DataProductDatasetAssociationFactory(
            data_product=data_product_2, dataset=dataset
        )
        response = client.get(ENDPOINT)
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 2
        assert len(response.json()["nodes"]) == 3

    def test_get_graph_data_only_data_products_one_link(self, client):
        data_product_1 = DataProductFactory()
        dataset = DatasetFactory(data_product=data_product_1)
        data_product_2 = DataProductFactory()
        DataProductDatasetAssociationFactory(
            data_product=data_product_2, dataset=dataset
        )
        response = client.get(ENDPOINT, params={"output_port_nodes_enabled": "false"})
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 1
        assert len(response.json()["nodes"]) == 2
