from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased, with_polymorphic

from app.abstract_data_product.input_ports.model import InputPort
from app.abstract_data_product.model import AbstractDataProduct
from app.abstract_data_product.type import AbstractDataProductType
from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.data_product_types.model import DataProductType
from app.configuration.domains.model import Domain
from app.core.logging import logger
from app.data_products.model import DataProduct
from app.data_products.output_ports.model import OutputPort
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
        adp = with_polymorphic(DataProduct, [])
        data_products = (
            self.db.execute(
                select(
                    adp.id.label("id"),
                    adp.name.label("name"),
                    adp.description.label("description"),
                    DataProductType.icon_key.label("icon_key"),
                    Domain.name.label("domain_name"),
                    Domain.id.label("domain_id"),
                )
                .select_from(adp)
                .join(DataProductType, adp.type_id == DataProductType.id, isouter=True)
                .join(Domain, adp.domain_id == Domain.id, isouter=True)
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
                    select(
                        AbstractDataProduct.id.label("id"),
                        AbstractDataProduct.name.label("name"),
                        AbstractDataProduct.description.label("description"),
                        Domain.name.label("domain_name"),
                        Domain.id.label("domain_id"),
                    )
                    .where(
                        AbstractDataProduct.abstract_data_product_type
                        == AbstractDataProductType.EXPLORATION
                    )
                    .join(
                        Domain, AbstractDataProduct.domain_id == Domain.id, isouter=True
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
                    select(
                        OutputPort.id.label("id"),
                        OutputPort.name.label("name"),
                        OutputPort.data_product_id.label("data_product_id"),
                        OutputPort.description.label("description"),
                        Domain.name.label("domain_name"),
                        Domain.id.label("domain_id"),
                    )
                    .select_from(OutputPort)
                    .join(
                        DataProduct,
                        OutputPort.data_product_id == DataProduct.id,
                        isouter=True,
                    )
                    .join(Domain, DataProduct.domain_id == Domain.id, isouter=True)
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
            consumer_abstract = aliased(AbstractDataProduct)
            abstract_data_product_links = (
                self.db.execute(
                    select(
                        InputPort.consuming_abstract_data_product_id.label(
                            "consumer_id"
                        ),
                        InputPort.output_port_id.label("dataset_id"),
                        InputPort.status.label("status"),
                    )
                    .select_from(InputPort)
                    .join(
                        consumer_abstract,
                        consumer_abstract.id
                        == InputPort.consuming_abstract_data_product_id,
                    )
                    .where(
                        consumer_abstract.abstract_data_product_type.in_(
                            data_product_types
                        )
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
                        animated=link["status"] == DecisionStatus.APPROVED.value,
                    )
                    for link in abstract_data_product_links
                ]
            )
        else:
            consumer_abstract = aliased(AbstractDataProduct)
            abstract_data_product_links = (
                self.db.execute(
                    select(
                        OutputPort.data_product_id.label("producer_id"),
                        InputPort.consuming_abstract_data_product_id.label(
                            "consumer_id"
                        ),
                        InputPort.status.label("status"),
                    )
                    .select_from(OutputPort)
                    .join(InputPort, InputPort.output_port_id == OutputPort.id)
                    .join(
                        consumer_abstract,
                        consumer_abstract.id
                        == InputPort.consuming_abstract_data_product_id,
                    )
                    .where(
                        consumer_abstract.abstract_data_product_type.in_(
                            data_product_types
                        )
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
                        animated=link["status"] == DecisionStatus.APPROVED.name,
                    )
                    for link in abstract_data_product_links
                ]
            )

        return Graph(nodes=set(nodes), edges=set(edges))
