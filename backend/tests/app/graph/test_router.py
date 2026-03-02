import pytest

from tests.factories import (
    DataProductDatasetAssociationFactory,
    DataProductFactory,
    DatasetFactory,
    DomainFactory,
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

    def test_data_products_only_arrow_points_producer_to_consumer(self, client):
        """Arrow should point from producer to consumer in Data Products only view."""
        producer = DataProductFactory()
        dataset = DatasetFactory(data_product=producer)
        consumer = DataProductFactory()
        DataProductDatasetAssociationFactory(data_product=consumer, dataset=dataset)
        response = client.get(ENDPOINT, params={"output_port_nodes_enabled": "false"})
        assert response.status_code == 200, response.text
        edge = response.json()["edges"][0]
        assert edge["source"] == str(producer.id), (
            "Edge source should be the producer (dataset owner)"
        )
        assert edge["target"] == str(consumer.id), (
            "Edge target should be the consumer (dataset reader)"
        )

    def test_graph_nodes_include_domain_fields(self, client):
        domain = DomainFactory()
        DataProductFactory(domain=domain)
        response = client.get(ENDPOINT, params={"output_port_nodes_enabled": "false"})
        assert response.status_code == 200, response.text
        node = next(
            n for n in response.json()["nodes"] if n["type"] == "dataProductNode"
        )
        assert node["data"]["domain_id"] == str(domain.id)
        assert node["data"]["domain"] == domain.name

    def test_output_port_inherits_domain_from_parent_data_product(self, client):
        domain = DomainFactory()
        data_product = DataProductFactory(domain=domain)
        DatasetFactory(data_product=data_product)
        response = client.get(ENDPOINT)
        assert response.status_code == 200, response.text
        dataset_node = next(
            n for n in response.json()["nodes"] if n["type"] == "datasetNode"
        )
        assert dataset_node["data"]["domain_id"] == str(domain.id)
        assert dataset_node["data"]["domain"] == domain.name

    def test_graph_nodes_from_different_domains(self, client):
        domain_a = DomainFactory()
        domain_b = DomainFactory()
        DataProductFactory(domain=domain_a)
        DataProductFactory(domain=domain_b)
        response = client.get(ENDPOINT, params={"output_port_nodes_enabled": "false"})
        assert response.status_code == 200, response.text
        nodes = response.json()["nodes"]
        assert len(nodes) == 2
        domain_ids = {n["data"]["domain_id"] for n in nodes}
        assert domain_ids == {str(domain_a.id), str(domain_b.id)}
