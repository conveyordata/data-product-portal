from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.logging.logger import logger
from app.data_outputs.model import DataOutput
from app.data_products.model import DataProduct
from app.datasets.model import Dataset
from app.domains.model import Domain
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.role_assignments.enums import DecisionStatus
from app.users.schema import User


class GraphService:
    def __init__(self):
        self.logger = logger

    def get_graph_data(
        self,
        db: Session,
        user: User,
        domain_nodes_enabled: bool = True,
        data_product_nodes_enabled: bool = True,
        dataset_nodes_enabled: bool = True,
        data_output_nodes_enabled: bool = True,
    ) -> Graph:
        # get all data products
        data_products = (
            db.scalars(
                select(DataProduct).options(
                    joinedload(DataProduct.dataset_links),
                    joinedload(DataProduct.data_outputs),
                )
            )
            .unique()
            .all()
        )
        # get all datasets
        datasets = (
            db.scalars(
                select(Dataset).options(
                    joinedload(Dataset.data_product_links),
                    joinedload(Dataset.data_output_links),
                )
            )
            .unique()
            .all()
        )
        # get all data outputs
        # get all domains - these will be group nodes
        domains = (
            db.scalars(
                select(Domain).options(
                    joinedload(Domain.datasets),
                    joinedload(Domain.data_products),
                )
            )
            .unique()
            .all()
        )
        data_outputs = (
            db.scalars(select(DataOutput).options(joinedload(DataOutput.dataset_links)))
            .unique()
            .all()
        )

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
                    members=[
                        membership.user.email
                        for membership in data_product_get.memberships
                        # TODO Don't use memberships here + take role into
                        # account + take pending status into account
                    ],
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
                    description=dataset_get.description,
                ),
                type=NodeType.datasetNode,
            )
            for dataset_get in datasets
        ]
        data_output_nodes = [
            Node(
                id=data_output.id,
                data=NodeData(
                    id=data_output.id,
                    name=data_output.name,
                    icon_key=data_output.configuration.configuration_type,
                    link_to_id=data_output.owner.id,
                    domain=data_output.owner.domain.name,
                    domain_id=data_output.owner.domain.id,
                    description=data_output.description,
                ),
                type=NodeType.dataOutputNode,
            )
            for data_output in data_outputs
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
        if data_output_nodes_enabled:
            nodes += data_output_nodes

        # Edges are the links between data products, datasets and data outputs
        edges: List[Edge] = []

        # Data products -- produce --> data outputs. This is a one-to-many.
        # Data outputs have a single owner.
        for data_output_get in data_outputs:
            data_output = data_output_get
            edges.append(
                Edge(
                    id=f"{data_output.owner.id}-{data_output.id}",
                    source=data_output.owner.id,
                    target=data_output.id,
                    animated=True,
                )
            )

        # Data outputs -- are bundled in --> data sets. Many-to-many.
        for dataset_get in datasets:
            dataset = dataset_get
            for data_output_link in dataset.data_output_links:
                data_output = data_output_link.data_output
                edges.append(
                    Edge(
                        id=f"{data_output.id}-{dataset.id}",
                        source=data_output.id,
                        target=dataset.id,
                        animated=data_output_link.status == DecisionStatus.APPROVED,
                    )
                )

        # Data sets -- are consumed by --> data products. Many-to-many.
        for data_product in data_products:
            for dataset_link in data_product.dataset_links:
                dataset = dataset_link.dataset
                edges.append(
                    Edge(
                        id=f"{data_product.id}-{dataset.id}",
                        source=dataset.id,
                        target=data_product.id,
                        animated=dataset_link.status == DecisionStatus.APPROVED,
                    )
                )

        # If certain nodes are disabled, we also need to redraw their edges.
        edges = self.reduce_edges(
            edges,
            dataset_nodes,
            data_product_nodes,
            data_output_nodes,
            dataset_nodes_enabled,
            data_product_nodes_enabled,
            data_output_nodes_enabled,
        )

        return Graph(nodes=set(nodes), edges=set(edges))

    def reduce_edges(
        self,
        edges: List[Edge],
        dataset_nodes: List[Node],
        data_product_nodes: List[Node],
        data_output_nodes: List[Node],
        dataset_nodes_enabled: bool,
        data_product_nodes_enabled: bool,
        data_output_nodes_enabled: bool,
    ) -> List[Edge]:
        """
        Reduce edges: for every disabled node:
        1) remove the edges that point to it and,
        2) make new ones that bridge the adjacent
           nodes (all source nodes need to point to all targets).
        """
        # Get all disabled nodes
        disabled_nodes: List[Node] = []
        if not dataset_nodes_enabled:
            disabled_nodes += dataset_nodes
        if not data_product_nodes_enabled:
            disabled_nodes += data_product_nodes
        if not data_output_nodes_enabled:
            disabled_nodes += data_output_nodes

        # Get all edges that point to or start from the disabled nodes
        for disabled_node in disabled_nodes:
            self.logger.debug(f"Processing disabled node {disabled_node.data.name}")
            source_edges: List[Edge] = []
            target_edges: List[Edge] = []
            source_nodes: List[str | UUID] = []
            target_nodes: List[str | UUID] = []
            for edge in edges:
                if edge.source == disabled_node.id:
                    # This edge starts from a disabled node, so we look at its target
                    self.logger.debug(
                        f"Edge {edge.id} starts from disabled node "
                        f"{disabled_node.data.name} and will be removed"
                    )
                    target_edges.append(edge)
                    self.logger.debug(
                        f"Adding {edge.source} to target "
                        f"nodes for {disabled_node.data.name}"
                    )
                    target_nodes.append(edge.target)
                if edge.target == disabled_node.id:
                    self.logger.debug(
                        f"Edge {edge.id} points to disabled node "
                        f"{disabled_node.data.name} and will be removed"
                    )
                    source_edges.append(edge)
                    self.logger.debug(
                        f"Adding {edge.source} to source nodes"
                        f" for {disabled_node.data.name}"
                    )
                    source_nodes.append(edge.source)
            # now we can create new edges between all source nodes and all target nodes
            is_animated = all([edge.animated for edge in source_edges + target_edges])
            for source_node in source_nodes:
                for target_node in target_nodes:
                    new_edge = Edge(
                        id=f"{source_node}-{target_node}",
                        source=source_node,
                        target=target_node,
                        animated=is_animated,
                    )
                    self.logger.debug(
                        f"Checking if new edge {new_edge.id} between "
                        f"{source_node} and {target_node} already exists"
                    )
                    if new_edge not in edges:
                        self.logger.debug(
                            f"Adding new edge {new_edge.id} between "
                            f"{source_node} and {target_node}"
                        )
                        edges.append(new_edge)
            # and remove the old edges
            for edge in source_edges + target_edges:
                self.logger.debug(
                    f"Removing edge {edge.id} between {edge.source} and {edge.target}"
                )
                edges.remove(edge)
            # then we process the next disabled node, with these new edges
        return edges
