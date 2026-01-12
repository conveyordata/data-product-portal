from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.graph.graph import Graph
from app.graph.service import GraphService

router = APIRouter(tags=["Graph"])


@router.get("")
def get_graph_data(
    db: Session = Depends(get_db_session),
    domain_nodes_enabled: bool = True,
    data_product_nodes_enabled: bool = True,
    dataset_nodes_enabled: bool = True,
) -> Graph:
    return GraphService(db).get_graph_data(
        domain_nodes_enabled=domain_nodes_enabled,
        data_product_nodes_enabled=data_product_nodes_enabled,
        dataset_nodes_enabled=dataset_nodes_enabled,
    )


_router = router
router = APIRouter()
old_route = "/graph"
route = "/v2/graph"
router.include_router(_router, prefix=old_route, deprecated=True)
router.include_router(_router, prefix=route)
