from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.configuration.domains.model import Domain
from app.core.logging import logger
from app.data_products.model import DataProduct
from app.datasets.model import Dataset
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.role_assignments.enums import DecisionStatus


class GraphService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger

    def get_graph_data(
        self,
        domain_nodes_enabled: bool = True,
        data_product_nodes_enabled: bool = True,
        dataset_nodes_enabled: bool = True,
    ) -> Graph:
        if not (data_product_nodes_enabled or dataset_nodes_enabled):
            return Graph(nodes=[], edges=[])
        domains = (
            self.db.scalars(
                select(Domain).options(
                    selectinload(Domain.datasets).selectinload(
                        Dataset.data_product_links
                    ),
                    selectinload(Domain.data_products).selectinload(
                        DataProduct.datasets
                    ),
                    selectinload(Domain.data_products).selectinload(
                        DataProduct.dataset_links
                    ),
                    selectinload(Domain.data_products).selectinload(
                        DataProduct.assignments
                    ),
                    selectinload(Domain.datasets).selectinload(
                        Dataset.data_product_links
                    ),
                )
            )
            .unique()
            .all()
        )
        datasets = {d for domain in domains for d in domain.datasets}
        data_products = {dp for domain in domains for dp in domain.data_products}

        # Nodes are { data products + datasets + data outputs }
        data_product_nodes = [
            Node(
                id=data_product_get.id,
                data=NodeData(
                    id=data_product_get.id,
                    name=data_product_get.name,
                    icon_key=data_product_get.type.icon_key,
                    link_to_id=data_product_get.id,
                    domain=data_product_get.domain.name,
                    domain_id=data_product_get.domain.id,
                    assignments=data_product_get.assignments,
                    description=data_product_get.description,
                ),
                type=NodeType.dataProductNode,
            )
            for data_product_get in data_products
        ]
        dataset_nodes = [
            Node(
                id=dataset_get.id,
                data=NodeData(
                    id=dataset_get.id,
                    name=dataset_get.name,
                    icon_key="dataset",
                    link_to_id=dataset_get.id,
                    domain=dataset_get.domain.name,
                    domain_id=dataset_get.domain.id,
                    # assignments=dataset_get.assignments,
                    description=dataset_get.description,
                ),
                type=NodeType.datasetNode,
            )
            for dataset_get in datasets
        ]

        domain_nodes = [
            Node(
                id=domain_get.id,
                data=NodeData(
                    id=domain_get.id,
                    name=domain_get.name,
                    link_to_id=domain_get.id,
                ),
                type=NodeType.domainNode,
            )
            for domain_get in domains
        ]

        nodes = []
        if domain_nodes_enabled:
            nodes += domain_nodes
        if data_product_nodes_enabled:
            nodes += data_product_nodes
        if dataset_nodes_enabled:
            nodes += dataset_nodes
        edges: List[Edge] = []
        if data_product_nodes_enabled and dataset_nodes_enabled:
            for dataset_get in datasets:
                dataset = dataset_get
                edges.append(
                    Edge(
                        id=f"{dataset.data_product_id}-{dataset.id}",
                        source=dataset.data_product_id,
                        target=dataset.id,
                        animated=True,
                    )
                )

            # Data sets -- are consumed by --> data products. Many-to-many.
            for data_product in data_products:
                for dataset_link in data_product.dataset_links:
                    dataset = dataset_link.dataset
                    edges.append(
                        Edge(
                            id=f"{dataset.id}-{data_product.id}",
                            source=dataset.id,
                            target=data_product.id,
                            animated=dataset_link.status == DecisionStatus.APPROVED,
                        )
                    )

        elif not dataset_nodes_enabled and data_product_nodes_enabled:
            # Data sets -- are consumed by --> data products. Many-to-many.
            for data_product in data_products:
                for dataset_link in data_product.dataset_links:
                    parent = dataset_link.dataset.data_product_id
                    edges.append(
                        Edge(
                            id=f"{parent}-{data_product.id}",
                            source=parent,
                            target=data_product.id,
                            animated=dataset_link.status == DecisionStatus.APPROVED,
                        )
                    )

        elif not data_product_nodes_enabled and dataset_nodes_enabled:
            for data_product in data_products:
                for dataset_link in data_product.dataset_links:
                    # If the data product has it's own dataset as children then we can show the link.
                    dataset = dataset_link.dataset
                    for consumer in data_product.datasets:
                        edges.append(
                            Edge(
                                id=f"{dataset.id}-{consumer.id}",
                                source=dataset.id,
                                target=consumer.id,
                                animated=dataset_link.status == DecisionStatus.APPROVED,
                            )
                        )
        else:
            edges = []
        return Graph(nodes=set(nodes), edges=set(edges))
