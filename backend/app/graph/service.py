from typing import List

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.abstract_data_product.type import AbstractDataProductType
from app.authorization.role_assignments.enums import DecisionStatus
from app.core.logging import logger
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType


class GraphService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger

    def get_graph_data(
        self,
        exploration_nodes_enabled: bool = False,
        output_port_nodes_enabled: bool = False,
    ) -> Graph:
        data_products = (
            self.db.execute(
                text(
                    """
                    SELECT
                        data_products.id as id,
                        adp.name as name,
                        adp.description as description,
                        data_product_types.icon_key as icon_key,
                        domains.name as domain_name,
                        domains.id as domain_id
                    FROM data_products
                    LEFT JOIN abstract_data_products as adp on data_products.id = adp.id
                    LEFT JOIN data_product_types on data_products.type_id = data_product_types.id
                    LEFT JOIN domains on adp.domain_id = domains.id
                    """
                )
            )
            .mappings()
            .all()
        )
        nodes = [
            Node(
                id=data_product["id"],
                data=NodeData(
                    id=data_product["id"],
                    name=data_product["name"],
                    icon_key=data_product["icon_key"],
                    domain=data_product["domain_name"],
                    domain_id=data_product["domain_id"],
                    description=data_product["description"],
                ),
                type=NodeType.dataProductNode,
            )
            for data_product in data_products
        ]
        edges: List[Edge] = []

        if exploration_nodes_enabled:
            exploration_nodes = (
                self.db.execute(
                    text(
                        """
                        SELECT explorations.id            as id,
                               adp.name                    as name,
                               adp.description             as description,
                               domains.name                as domain_name,
                               domains.id                  as domain_id
                        FROM explorations
                        LEFT JOIN abstract_data_products as adp on explorations.id = adp.id
                        LEFT JOIN domains on adp.domain_id = domains.id
                        """
                    )
                )
                .mappings()
                .all()
            )
            nodes.extend(
                [
                    Node(
                        id=exploration["id"],
                        data=NodeData(
                            id=exploration["id"],
                            name=exploration["name"],
                            domain=exploration["domain_name"],
                            domain_id=exploration["domain_id"],
                            description=exploration["description"],
                        ),
                        type=NodeType.explorationNode,
                    )
                    for exploration in exploration_nodes
                ]
            )

        data_product_types = (
            [AbstractDataProductType.EXPLORATION, AbstractDataProductType.DATA_PRODUCT]
            if exploration_nodes_enabled
            else [AbstractDataProductType.DATA_PRODUCT]
        )

        if output_port_nodes_enabled:
            datasets = (
                self.db.execute(
                    text(
                        """
                SELECT datasets.id            as id,
                       datasets.name          as name,
                       datasets.data_product_id   as data_product_id,
                       datasets.description   as description,
                       domains.name                as domain_name,
                       domains.id                  as domain_id
                FROM datasets
                LEFT JOIN data_products on data_products.id = datasets.data_product_id
                LEFT JOIN abstract_data_products as adp on data_products.id = adp.id
                LEFT JOIN domains on adp.domain_id = domains.id
                """
                    )
                )
                .mappings()
                .all()
            )

            nodes.extend(
                [
                    Node(
                        id=dataset["id"],
                        data=NodeData(
                            id=dataset["id"],
                            name=dataset["name"],
                            icon_key="dataset",
                            link_to_id=dataset["data_product_id"],
                            domain=dataset["domain_name"],
                            domain_id=dataset["domain_id"],
                            description=dataset["description"],
                        ),
                        type=NodeType.outputPortNode,
                    )
                    for dataset in datasets
                ]
            )
            edges.extend(
                [
                    Edge(
                        id=f"{dataset['data_product_id']}-{dataset['id']}",
                        source=dataset["data_product_id"],
                        target=dataset["id"],
                        animated=True,
                    )
                    for dataset in datasets
                ]
            )
            abstract_data_product_links = (
                self.db.execute(
                    text(
                        """
                SELECT input_ports.consuming_abstract_data_product_id as consumer_id,
                       input_ports.dataset_id as dataset_id,
                       input_ports.status          as status
                FROM input_ports
                JOIN abstract_data_products on abstract_data_products.id = input_ports.consuming_abstract_data_product_id
                WHERE abstract_data_products.abstract_data_product_type in :data_product_types
                """
                    ).bindparams(bindparam("data_product_types", expanding=True)),
                    {"data_product_types": data_product_types},
                )
                .mappings()
                .all()
            )
            edges.extend(
                [
                    Edge(
                        id=f"{link['dataset_id']}-{link['consumer_id']}",
                        source=link["dataset_id"],
                        target=link["consumer_id"],
                        animated=link["status"] == DecisionStatus.APPROVED.name,
                    )
                    for link in abstract_data_product_links
                ]
            )
        else:
            abstract_data_product_links = (
                self.db.execute(
                    text(
                        """
                        SELECT data_products.id          as producer_id,
                               abstract_data_products.id as consumer_id,
                               input_ports.status        as status
                        FROM data_products
                                 JOIN datasets ON data_products.id = datasets.data_product_id
                                 JOIN input_ports ON datasets.id = input_ports.dataset_id
                                 JOIN abstract_data_products
                                      ON abstract_data_products.id = input_ports.consuming_abstract_data_product_id
                        WHERE abstract_data_products.abstract_data_product_type IN :data_product_types
                        """
                    ).bindparams(bindparam("data_product_types", expanding=True)),
                    {"data_product_types": data_product_types},
                )
                .mappings()
                .all()
            )
            edges.extend(
                [
                    Edge(
                        id=f"{link['producer_id']}-{link['consumer_id']}",
                        source=link["producer_id"],
                        target=link["consumer_id"],
                        animated=link["status"] == DecisionStatus.APPROVED.name,
                    )
                    for link in abstract_data_product_links
                ]
            )

        return Graph(nodes=set(nodes), edges=set(edges))
