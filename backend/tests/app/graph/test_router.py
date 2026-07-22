from tests.factories import (
    DataProductFactory,
    DomainFactory,
    ExplorationFactory,
    InputPortFactory,
    OutputPortFactory,
    TechnicalAssetFactory,
)

ENDPOINT = "/api/v2/graph"


class TestGraphRouter:
    def test_get_graph_data(self, client):
        domain = DomainFactory()
        data_product = DataProductFactory(domain=domain)
        exp = ExplorationFactory(domain=domain)
        dataset = OutputPortFactory(data_product=data_product)
        InputPortFactory(output_port=dataset, consuming_abstract_data_product=exp)
        TechnicalAssetFactory(owner=data_product)
        response = client.get(ENDPOINT)
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 0
        assert len(response.json()["nodes"]) == 1
        for node in response.json()["nodes"]:
            assert node["data"]["domain_id"] == str(domain.id)
            assert node["data"]["domain"] == domain.name

    def test_get_graph_data_include_output_ports(self, client):
        domain = DomainFactory()
        data_product = DataProductFactory(domain=domain)
        exp = ExplorationFactory(domain=domain)
        dataset = OutputPortFactory(data_product=data_product)
        InputPortFactory(output_port=dataset, consuming_abstract_data_product=exp)
        TechnicalAssetFactory(owner=data_product)
        response = client.get(ENDPOINT, params={"output_port_nodes_enabled": "true"})
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 1
        assert len(response.json()["nodes"]) == 2
        for node in response.json()["nodes"]:
            assert node["data"]["domain_id"] == str(domain.id)
            assert node["data"]["domain"] == domain.name

    def test_get_graph_data_include_explorations(self, client):
        domain = DomainFactory()
        data_product = DataProductFactory(domain=domain)
        exp = ExplorationFactory(domain=domain)
        dataset = OutputPortFactory(data_product=data_product)
        InputPortFactory(output_port=dataset, consuming_abstract_data_product=exp)
        response = client.get(ENDPOINT, params={"exploration_nodes_enabled": "true"})
        assert response.status_code == 200, response.text
        assert len(response.json()["nodes"]) == 2

    def test_get_graph_data_include_output_ports_and_explorations(self, client):
        domain = DomainFactory()
        data_product = DataProductFactory(domain=domain)
        exp = ExplorationFactory(domain=domain)
        dataset = OutputPortFactory(data_product=data_product)
        InputPortFactory(output_port=dataset, consuming_abstract_data_product=exp)
        response = client.get(
            ENDPOINT,
            params={
                "output_port_nodes_enabled": "true",
                "exploration_nodes_enabled": "true",
            },
        )
        assert response.status_code == 200, response.text
        assert len(response.json()["nodes"]) == 3

    def test_get_graph_data_single_consumer_show_output_ports(self, client):
        data_product_1 = DataProductFactory()
        dataset = OutputPortFactory(data_product=data_product_1)
        data_product_2 = DataProductFactory()
        InputPortFactory(
            consuming_abstract_data_product=data_product_2, output_port=dataset
        )
        response = client.get(ENDPOINT, params={"output_port_nodes_enabled": "true"})
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 2
        assert len(response.json()["nodes"]) == 3

    def test_get_graph_data_single_consumer(self, client):
        data_product_1 = DataProductFactory()
        dataset = OutputPortFactory(data_product=data_product_1)
        data_product_2 = DataProductFactory()
        InputPortFactory(
            consuming_abstract_data_product=data_product_2, output_port=dataset
        )
        response = client.get(ENDPOINT)
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 1
        assert len(response.json()["nodes"]) == 2

    def test_data_products_only_arrow_points_producer_to_consumer(self, client):
        """Arrow should point from producer to consumer in Data Products only view."""
        producer = DataProductFactory()
        dataset = OutputPortFactory(data_product=producer)
        consumer = DataProductFactory()
        InputPortFactory(consuming_abstract_data_product=consumer, output_port=dataset)
        response = client.get(ENDPOINT, params={"output_port_nodes_enabled": "false"})
        assert response.status_code == 200, response.text
        edge = response.json()["edges"][0]
        assert edge["source"] == str(producer.id), (
            "Edge source should be the producer (dataset owner)"
        )
        assert edge["target"] == str(consumer.id), (
            "Edge target should be the consumer (dataset reader)"
        )
