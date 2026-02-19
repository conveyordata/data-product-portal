import pytest

from tests.factories import DataProductFactory, DatasetFactory, TechnicalAssetFactory

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
    def test_get_graph_data_old(self, client, route):
        data_product = DataProductFactory()
        DatasetFactory(data_product=data_product)
        TechnicalAssetFactory(owner=data_product)
        response = client.get(route)
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 1
        assert len(response.json()["nodes"]) == 3
