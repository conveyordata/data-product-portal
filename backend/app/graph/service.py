from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session, defer, joinedload, selectinload

from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.domains.model import Domain
from app.core.logging import logger
from app.data_products.model import DataProduct
from app.data_products.output_ports.input_ports.model import (
    DataProductDatasetAssociation,
)
from app.data_products.output_ports.model import Dataset
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType


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

        nodes = []
        if domain_nodes_enabled:
            domains = self.db.scalars(select(Domain)).unique().all()
            nodes.extend(
                [
                    Node(
                        id=domain_get.id,
                        data=NodeData(
                            id=domain_get.id,
                            name=domain_get.name,
                        ),
                        type=NodeType.domainNode,
                    )
                    for domain_get in domains
                ]
            )
        if data_product_nodes_enabled or dataset_nodes_enabled:
            data_products = (
                self.db.scalars(
                    select(DataProduct).options(
                        selectinload(DataProduct.datasets)
                        .defer(Dataset.data_product_count)
                        .defer(Dataset.technical_assets_count),
                        selectinload(DataProduct.dataset_links).joinedload(
                            DataProductDatasetAssociation.data_product
                        ),
                        selectinload(DataProduct.assignments),
                        joinedload(DataProduct.domain),
                    )
                )
                .unique()
                .all()
            )

        # data_products = {dp for domain in domains for dp in domain.data_products}
        if data_product_nodes_enabled:
            nodes.extend(
                [
                    Node(
                        id=data_product_get.id,
                        data=NodeData(
                            id=data_product_get.id,
                            name=data_product_get.name,
                            icon_key=data_product_get.type.icon_key,
                            domain=data_product_get.domain.name,
                            domain_id=data_product_get.domain.id,
                            assignments=data_product_get.assignments,
                            description=data_product_get.description,
                        ),
                        type=NodeType.dataProductNode,
                    )
                    for data_product_get in data_products
                ]
            )
        if dataset_nodes_enabled:
            # get all datasets
            datasets = (
                self.db.scalars(
                    select(Dataset).options(
                        defer(Dataset.data_product_count),
                        defer(Dataset.technical_assets_count),
                        joinedload(Dataset.data_product).joinedload(DataProduct.domain),
                    )
                )
                .unique()
                .all()
            )
            nodes.extend(
                [
                    Node(
                        id=dataset_get.id,
                        data=NodeData(
                            id=dataset_get.id,
                            name=dataset_get.name,
                            icon_key="dataset",
                            link_to_id=dataset_get.data_product.id,
                            domain=dataset_get.data_product.domain.name,
                            domain_id=dataset_get.data_product.domain.id,
                            # assignments=dataset_get.assignments,
                            description=dataset_get.description,
                        ),
                        type=NodeType.datasetNode,
                    )
                    for dataset_get in datasets
                ]
            )
        edges: List[Edge] = []
        if data_product_nodes_enabled and dataset_nodes_enabled:
            edges.extend(
                [
                    Edge(
                        id=f"{dataset.data_product_id}-{dataset.id}",
                        source=dataset.data_product_id,
                        target=dataset.id,
                        animated=True,
                    )
                    for dataset in datasets
                ]
            )

            # Data sets -- are consumed by --> data products. Many-to-many.
            for data_product in data_products:
                edges.extend(
                    Edge(
                        id=f"{dataset_link.dataset_id}-{data_product.id}",
                        source=dataset_link.dataset_id,
                        target=data_product.id,
                        animated=dataset_link.status == DecisionStatus.APPROVED,
                    )
                    for dataset_link in data_product.dataset_links
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
                    edges.extend(
                        [
                            Edge(
                                id=f"{dataset_link.dataset_id}-{consumer.id}",
                                source=dataset_link.dataset_id,
                                target=consumer.id,
                                animated=dataset_link.status == DecisionStatus.APPROVED,
                            )
                            for consumer in data_product.datasets
                        ]
                    )
        else:
            edges = []
        return Graph(nodes=set(nodes), edges=set(edges))
