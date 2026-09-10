from app.authorization.roles.schema import Scope
from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProductVisibility
from app.data_products.output_ports.enums import OutputPortAccessType
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetRoleAssignmentFactory,
    DomainFactory,
    ExplorationFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    TechnicalAssetFactory,
    UserFactory,
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

    def test_get_graph_data__filters_hidden_data_product(self, client):
        data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
        DataProductFactory(visibility=DataProductVisibility.HIDDEN)
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[AuthorizationAction.DATA_PRODUCT__READ_INTEGRATIONS],
        )
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
        )
        response = client.get(ENDPOINT)
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 0
        assert len(response.json()["nodes"]) == 1

    def test_get_graph_data__filters_private_output_ports(self, client):
        output_port = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_QUERY_STATS],
        )
        DatasetRoleAssignmentFactory(
            output_port_id=output_port.id,
            user_id=user.id,
            role_id=role.id,
        )
        response = client.get(ENDPOINT, params={"output_port_nodes_enabled": "true"})
        assert response.status_code == 200, response.text
        assert len(response.json()["edges"]) == 1, (
            "We expect 1 edge between the data product and the accessible private output port"
        )
        assert len(response.json()["nodes"]) == 3, (
            "We expect 2 nodes 2 data products and 1 output port"
        )

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
