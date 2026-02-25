from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.graph.graph import Graph
from app.graph.service import GraphService

router = APIRouter(tags=["Graph"])


@router.get("/graph", deprecated=True)
def get_graph_data_old(
    db: Session = Depends(get_db_session),
    data_product_nodes_enabled: bool = True,
    dataset_nodes_enabled: bool = True,
) -> Graph:
    return GraphService(db).get_graph_data(
        data_product_nodes_enabled=data_product_nodes_enabled,
        dataset_nodes_enabled=dataset_nodes_enabled,
    )


@router.get("/v2/graph")
def get_graph_data(
    db: Session = Depends(get_db_session),
    data_product_nodes_enabled: bool = True,
    output_port_nodes_enabled: bool = True,
) -> Graph:
    return GraphService(db).get_graph_data(
        data_product_nodes_enabled=data_product_nodes_enabled,
        dataset_nodes_enabled=output_port_nodes_enabled,
    )
