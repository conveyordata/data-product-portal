from tests.factories import DataOutputFactory, DataProductFactory, DatasetFactory

ENDPOINT = "/api/graph"


class TestGraphRouter:
    def test_get_graph_data(self, client):
        data_product = DataProductFactory()
        DatasetFactory(data_product=data_product)
        DataOutputFactory(owner=data_product)
        response = client.get(ENDPOINT)
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 1
        assert len(response.json()["nodes"]) == 4
