from tests.factories import DataOutputFactory, DataProductFactory, DatasetFactory

ENDPOINT = "/api/graph"


class TestGraphRouter:
    def test_get_graph_data(self, client):
        data_product = DataProductFactory()
        DatasetFactory()
        DataOutputFactory(owner=data_product)
        response = client.get(f"{ENDPOINT}")
        assert len(response.json()["edges"]) == 1
        assert len(response.json()["nodes"]) == 3
