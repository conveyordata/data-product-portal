from sqlalchemy.orm import Session

from app.data_outputs.service import DataOutputService
from app.data_products.service import DataProductService
from app.datasets.service import DatasetService
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.role_assignments.enums import DecisionStatus
from app.users.schema import User


class GraphService:
    def get_graph_data(self, db: Session, user: User) -> Graph:
        # get all data products
        data_product_gets = DataProductService().get_data_products(db=db)
        # get all datasets
        dataset_gets = DatasetService().get_datasets(db=db, user=user)
        # get all data outputs
        data_outputs = DataOutputService().get_data_outputs(db=db)

        # Nodes are { data products + datasets + data outputs }
        data_product_nodes = [
            Node(
                id=data_product_get.id,
                data=NodeData(
                    id=data_product_get.id,
                    name=data_product_get.name,
                    icon_key=data_product_get.type.icon_key,
                    link_to_id=data_product_get.id,
                ),
                type=NodeType.dataProductNode,
            )
            for data_product_get in data_product_gets
        ]
        dataset_nodes = [
            Node(
                id=dataset_get.id,
                data=NodeData(
                    id=dataset_get.id, name=dataset_get.name, icon_key="dataset"
                ),
                type=NodeType.datasetNode,
                link_to_id=dataset_get.id,
            )
            for dataset_get in dataset_gets
        ]
        data_output_nodes = [
            Node(
                id=data_output.id,
                data=NodeData(
                    id=data_output.id,
                    name=data_output.name,
                    icon_key=data_output.configuration.configuration_type,
                    link_to_id=data_output.owner.id,
                ),
                type=NodeType.dataOutputNode,
            )
            for data_output in data_outputs
        ]

        nodes = data_product_nodes + dataset_nodes + data_output_nodes

        # Edges are the links between data products, datasets and data outputs
        edges = []

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
        for dataset_get in dataset_gets:
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
        for data_product in data_product_gets:
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

        return Graph(nodes=set(nodes), edges=set(edges))
