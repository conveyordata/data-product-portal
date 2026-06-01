from typing import TYPE_CHECKING, cast

from app.abstract_data_product.model import AbstractDataProduct, AbstractDataProductType
from app.graph.node import Node, NodeData, NodeType

if TYPE_CHECKING:
    from app.data_products.model import DataProduct


def get_graph_data_from_abstract_data_product(
    id: str, adp: AbstractDataProduct
) -> Node:
    icon = None
    node_type = NodeType.dataProductNode
    match adp.abstract_data_product_type:
        case AbstractDataProductType.DATA_PRODUCT:
            data_product = cast("DataProduct", adp)
            icon = data_product.type.icon_key
            node_type = NodeType.dataProductNode
        case AbstractDataProductType.EXPLORATION:
            node_type = NodeType.explorationNode
        case _:
            raise Exception(
                f"Unsupported abstract data product type: {adp.abstract_data_product_type}"
            )
    return Node(
        id=id,
        data=NodeData(
            id=f"{adp.id}",
            icon_key=icon,
            name=adp.name,
        ),
        type=node_type,
    )
