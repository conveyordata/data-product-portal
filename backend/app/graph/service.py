from typing import List

from sqlalchemy import text
from sqlalchemy.orm import Session

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
        data_product_nodes_enabled: bool = True,
        dataset_nodes_enabled: bool = True,
    ) -> Graph:
        if not data_product_nodes_enabled and not dataset_nodes_enabled:
            raise ValueError(
                "At least one of dataproduct_nodes_enabled or dataset_nodes_enabled must be True"
            )
        nodes: List[Node] = []
        if data_product_nodes_enabled:
            data_products = (
                self.db.execute(
                    text(
                        """
                SELECT
                    data_products.id as id,
                    data_products.name as name,
                    data_products.description as description,
                    data_product_types.icon_key as icon_key,
                    domains.name as domain_name,
                    domains.id as domain_id
                FROM data_products
                LEFT JOIN data_product_types on data_products.type_id = data_product_types.id
                LEFT JOIN domains on data_products.domain_id = domains.id
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
                        # assignments=data_product_get.assignments,
                        description=data_product["description"],
                    ),
                    type=NodeType.dataProductNode,
                )
                for data_product in data_products
            ]
        edges: List[Edge] = []
        datasets = []
        if dataset_nodes_enabled:
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
                LEFT JOIN domains on data_products.domain_id = domains.id
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
                        type=NodeType.datasetNode,
                    )
                    for dataset in datasets
                ]
            )
        if data_product_nodes_enabled and dataset_nodes_enabled:
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
            data_product_links = (
                self.db.execute(
                    text(
                        """
                SELECT data_products_datasets.data_product_id as consumer_id,
                       data_products_datasets.dataset_id as dataset_id,
                       data_products_datasets.status          as status
                FROM data_products_datasets
                """
                    )
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
                        animated=link.status == DecisionStatus.APPROVED,
                    )
                    for link in data_product_links
                ]
            )

        elif data_product_nodes_enabled:
            data_product_links = (
                self.db.execute(
                    text(
                        """
                SELECT
                    data_products.id as producer_id,
                    data_products_datasets.data_product_id as consumer_id,
                    data_products_datasets.status as status
                FROM data_products
                JOIN datasets on data_products.id = datasets.data_product_id
                JOIN data_products_datasets on datasets.id = data_products_datasets.dataset_id
                """
                    )
                )
                .mappings()
                .all()
            )
            edges.extend(
                [
                    Edge(
                        id=f"{link['consumer_id']}-{link['producer_id']}",
                        source=link["consumer_id"],
                        target=link["producer_id"],
                        animated=link["status"] == DecisionStatus.APPROVED,
                    )
                    for link in data_product_links
                ]
            )
        else:
            # Only dataset nodes enabled
            data_product_links = (
                self.db.execute(
                    text(
                        """
                SELECT
                    datasets.id as consumer_id,
                    data_products_datasets.dataset_id as producer_id,
                    data_products_datasets.status as status
                FROM data_products_datasets
                JOIN datasets on datasets.data_product_id = data_products_datasets.data_product_id
                """
                    )
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
                        animated=link.status == DecisionStatus.APPROVED,
                    )
                    for link in data_product_links
                ]
            )

        return Graph(nodes=set(nodes), edges=set(edges))
